#!/usr/bin/env python3
"""
FastAPI server for computer control.
Runs as regular user and communicates with privileged subprocess.
"""

import subprocess
import json
import os
import sys
import io
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import base64
import httpx


# Request models
class MouseMoveRequest(BaseModel):
    x: int
    y: int


class MouseButtonRequest(BaseModel):
    button: str = "left"  # left, right, middle


class MouseClickRequest(BaseModel):
    x: int
    y: int
    button: str = "left"


class MouseDragDropRequest(BaseModel):
    x: int
    y: int
    x_drop: int
    y_drop: int
    button: str = "left"


class KeyPressRequest(BaseModel):
    key: str


class KeyTypeRequest(BaseModel):
    text: str


class CroppedScreenshotRequest(BaseModel):
    x: int
    y: int
    width: int
    height: int


class ExecuteActionRequest(BaseModel):
    action_type: str
    parameters: Dict[str, Any]


class AIRequest(BaseModel):
    messages: list
    provider: str = "openai"  # "openai" or "gemini"
    model: str = "gpt-4-vision-preview"
    max_tokens: int = 500
    temperature: float = 0.3
    api_key: Optional[str] = None  # Optional API key from frontend (overrides env var)
    thinking_budget: Optional[int] = None  # Thinking budget for Gemini models
    media_resolution: Optional[str] = None  # Media resolution: "low", "medium", "high"


class PrivilegedWorkerManager:
    """Manages the privileged worker subprocess."""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.worker_script = Path(__file__).parent / "privileged_worker.py"
        
    def start(self):
        """Start the privileged worker subprocess."""
        if self.process is not None:
            return
            
        # Check if script exists
        if not self.worker_script.exists():
            raise RuntimeError(f"Worker script not found: {self.worker_script}")
        
        # Start subprocess with sudo (requires password or NOPASSWD in sudoers)
        # Alternative: run with setuid or use a different privilege escalation method
        try:
            # Try to start with sudo
            self.process = subprocess.Popen(
                ["sudo", sys.executable, str(self.worker_script)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        except Exception as e:
            # If sudo fails, try without (for testing or if already running with privileges)
            try:
                self.process = subprocess.Popen(
                    [sys.executable, str(self.worker_script)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
            except Exception as e2:
                raise RuntimeError(f"Failed to start worker: {e2}")
    
    def stop(self):
        """Stop the privileged worker subprocess."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
    
    def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send a command to the worker and get response."""
        if self.process is None:
            self.start()
        
        if self.process.poll() is not None:
            # Process died, restart it
            self.start()
        
        try:
            # Send command
            command_json = json.dumps(command) + "\n"
            self.process.stdin.write(command_json)
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline()
            if not response_line:
                raise RuntimeError("Worker process ended unexpectedly")
            
            response = json.loads(response_line.strip())
            return response
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid response from worker: {e}")
        except Exception as e:
            raise RuntimeError(f"Error communicating with worker: {e}")


# Setup logging to file
log_file = "/tmp/computer_use_server.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)  # Also log to console
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Server logging to {log_file}")

# Global worker manager
worker_manager = PrivilegedWorkerManager()

# FastAPI app
app = FastAPI(title="Computer Control API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.on_event("startup")
async def startup_event():
    """Start the privileged worker on startup."""
    try:
        logger.info("Starting privileged worker...")
        worker_manager.start()
        logger.info("Privileged worker started successfully")
    except Exception as e:
        logger.error(f"Could not start privileged worker: {e}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the privileged worker on shutdown."""
    logger.info("Shutting down server...")
    worker_manager.stop()
    logger.info("Server shutdown complete")


@app.get("/")
async def root():
    """Serve the frontend."""
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Computer Control API", "status": "running"}


@app.get("/status")
async def get_status():
    """Get current status including safety mode."""
    try:
        result = worker_manager.send_command({"action": "status"})
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/screenshot")
async def screenshot():
    """Take a screenshot."""
    try:
        logger.info("Screenshot requested")
        result = worker_manager.send_command({"action": "screenshot"})
        if result.get("success"):
            logger.debug("Screenshot captured successfully")
            return result
        else:
            logger.error(f"Screenshot failed: {result.get('error', 'Unknown error')}")
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mouse/move")
async def mouse_move(request: MouseMoveRequest):
    """Move mouse to coordinates."""
    try:
        result = worker_manager.send_command({
            "action": "mouse_move",
            "x": request.x,
            "y": request.y
        })
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mouse/button/down")
async def mouse_button_down(request: MouseButtonRequest):
    """Press mouse button down."""
    try:
        result = worker_manager.send_command({
            "action": "mouse_button_down",
            "button": request.button
        })
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mouse/button/up")
async def mouse_button_up(request: MouseButtonRequest):
    """Release mouse button."""
    try:
        result = worker_manager.send_command({
            "action": "mouse_button_up",
            "button": request.button
        })
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mouse/click")
async def mouse_click(request: MouseClickRequest):
    """Click at coordinates."""
    try:
        result = worker_manager.send_command({
            "action": "mouse_click",
            "x": request.x,
            "y": request.y,
            "button": request.button
        })
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mouse/drag_drop")
async def mouse_drag_drop(request: MouseDragDropRequest):
    """Drag from (x, y) to (x_drop, y_drop)."""
    try:
        result = worker_manager.send_command({
            "action": "mouse_drag_drop",
            "x": request.x,
            "y": request.y,
            "x_drop": request.x_drop,
            "y_drop": request.y_drop,
            "button": request.button
        })
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/keyboard/press")
async def key_press(request: KeyPressRequest):
    """Press a key."""
    try:
        result = worker_manager.send_command({
            "action": "key_press",
            "key": request.key
        })
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/keyboard/type")
async def key_type(request: KeyTypeRequest):
    """Type a string."""
    try:
        result = worker_manager.send_command({
            "action": "key_type",
            "text": request.text
        })
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/keyboard/page_up")
async def page_up():
    """Press Page Up key."""
    try:
        result = worker_manager.send_command({
            "action": "key_press",
            "key": "page_up"
        })
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/keyboard/page_down")
async def page_down():
    """Press Page Down key."""
    try:
        result = worker_manager.send_command({
            "action": "key_press",
            "key": "page_down"
        })
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/screenshot/crop")
async def cropped_screenshot(request: CroppedScreenshotRequest):
    """Get a cropped portion of the screenshot."""
    try:
        # Get full screenshot
        result = worker_manager.send_command({"action": "screenshot"})
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
        
        # Decode the image
        import io
        from PIL import Image
        img_data = base64.b64decode(result["image"])
        img = Image.open(io.BytesIO(img_data))
        
        # Crop the image
        # Ensure coordinates are within bounds
        x = max(0, min(request.x, img.width))
        y = max(0, min(request.y, img.height))
        width = max(1, min(request.width, img.width - x))
        height = max(1, min(request.height, img.height - y))
        
        cropped = img.crop((x, y, x + width, y + height))
        
        # Convert back to base64
        buffer = io.BytesIO()
        cropped.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        return {
            "success": True,
            "image": img_base64,
            "width": width,
            "height": height,
            "x": x,
            "y": y
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute_action")
async def execute_action(request: ExecuteActionRequest):
    """Execute an action from the AI model. Returns success status or error."""
    try:
        action_type = request.action_type
        params = request.parameters
        
        command = None
        
        if action_type == "click":
            command = {
                "action": "mouse_click",
                "x": params.get("x"),
                "y": params.get("y"),
                "button": params.get("button", "left")
            }
        elif action_type == "type":
            command = {
                "action": "key_type",
                "text": params.get("text", "")
            }
        elif action_type == "key_press":
            command = {
                "action": "key_press",
                "key": params.get("key")
            }
        elif action_type == "drag_drop":
            command = {
                "action": "mouse_drag_drop",
                "x": params.get("x"),
                "y": params.get("y"),
                "x_drop": params.get("x_drop"),
                "y_drop": params.get("y_drop"),
                "button": params.get("button", "left")
            }
        elif action_type == "move":
            command = {
                "action": "mouse_move",
                "x": params.get("x"),
                "y": params.get("y")
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action type: {action_type}")
        
        result = worker_manager.send_command(command)
        if result.get("success"):
            logger.info(f"Action {action_type} executed successfully")
        else:
            logger.warning(f"Action {action_type} failed: {result.get('error', 'Unknown error')}")
        return result
        
    except Exception as e:
        logger.error(f"Error executing action {action_type}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/chat")
async def ai_chat(request: AIRequest):
    """Proxy for AI APIs (OpenAI or Gemini) to avoid CORS issues."""
    provider = request.provider.lower()
    
    try:
        if provider == "openai":
            return await _handle_openai(request)
        elif provider == "gemini":
            return await _handle_gemini(request)
        else:
            logger.error(f"Unknown provider: {provider}")
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}. Use 'openai' or 'gemini'")
    except HTTPException:
        # Re-raise HTTPExceptions (already logged in handlers)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ai_chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def _handle_openai(request: AIRequest):
    """Handle OpenAI API requests - simple proxy."""
    api_key = request.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not provided")
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not provided in request or environment variable")
    
    try:
        logger.debug(f"Calling OpenAI API with model {request.model}, {len(request.messages)} messages")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": request.model,
                    "messages": request.messages,
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature
                },
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(f"OpenAI API response received: {len(result.get('choices', []))} choices")
            return result
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenAI API HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"OpenAI API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def _handle_gemini(request: AIRequest):
    """Handle Google Gemini API requests - simple proxy with minimal format conversion."""
    try:
        from google import genai
    except ImportError:
        raise HTTPException(
            status_code=500, 
            detail="google-genai package not installed. Run: pip install google-genai"
        )
    
    api_key = request.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not provided")
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not provided in request or environment variable")
    
    try:
        logger.debug(f"Calling Gemini API with model {request.model}, thinking_budget={request.thinking_budget}")
        client = genai.Client(api_key=api_key)
        
        model_name = request.model if request.model else "gemini-1.5-pro"
        
        # Convert OpenAI format to Gemini format according to generate_content API spec
        # Structure: contents = [Content, ...] where Content = {parts: [Part, ...], role: "user"|"model"}
        contents = []
        
        for msg in request.messages:
            role = msg.get("role", "user")
            # Map OpenAI roles to Gemini roles
            gemini_role = "user" if role == "user" else "model"
            
            content = msg.get("content", "")
            parts = []
            
            if isinstance(content, list):
                # Multi-part content (text + images)
                for part in content:
                    if part.get("type") == "text":
                        parts.append({"text": part.get("text", "")})
                    elif part.get("type") == "image_url":
                        image_url = part.get("image_url", {}).get("url", "")
                        if image_url.startswith("data:image"):
                            # Parse data URL: data:image/png;base64,<data>
                            header, data = image_url.split(",", 1)
                            # Extract mime type from header (e.g., "data:image/png;base64" -> "image/png")
                            mime_type = "image/png"  # default
                            if "image/" in header:
                                mime_part = header.split("image/")[1].split(";")[0]
                                mime_type = f"image/{mime_part}"
                            
                            parts.append({
                                "inlineData": {
                                    "mimeType": mime_type,
                                    "data": data  # Already base64 encoded
                                }
                            })
            else:
                # Simple string content
                parts.append({"text": str(content)})
            
            if parts:
                contents.append({
                    "role": gemini_role,
                    "parts": parts
                })
        
        # Build generationConfig according to API spec
        generation_config = {}
        if request.temperature is not None:
            generation_config["temperature"] = request.temperature
        if request.max_tokens is not None:
            generation_config["maxOutputTokens"] = request.max_tokens
        if request.thinking_budget is not None:
            # thinkingBudget goes inside thinkingConfig
            generation_config["thinkingConfig"] = {
                "thinkingBudget": request.thinking_budget
            }
        
        # Generate response using new API format
        try:
            request_body = {
                "contents": contents
            }
            if generation_config:
                request_body["config"] = generation_config
            
            response = client.models.generate_content(
                model=model_name,
                **request_body
            )
        except Exception as gen_error:
            logger.error(f"Gemini generate_content failed: {gen_error}", exc_info=True)
            raise
        
        # Check if response has content
        if not response or not hasattr(response, 'text') or not response.text:
            error_msg = "Gemini API returned empty response"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        logger.debug(f"Gemini API response received successfully")
        
        # Convert to OpenAI-like format for compatibility
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": response.text
                }
            }]
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions (already logged)
        raise
    except Exception as e:
        logger.error(f"Gemini API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting FastAPI server on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)  # Use our custom logging

