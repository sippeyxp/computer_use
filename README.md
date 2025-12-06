# Computer Control API

A FastAPI server that provides remote control capabilities for screenshots, mouse events, and keyboard input on Linux. The privileged operations (screenshot and input simulation) run in a separate subprocess that requires elevated privileges.

Includes a web frontend for AI-powered computer automation tasks.

## Features

- **Screenshots**: Capture the entire screen
- **Mouse Control**: Move, click, drag & drop, button up/down
- **Keyboard Control**: Type text, press keys (including special keys like Page Up/Down)
- **Safety Mechanism**: F9 key acts as a safety lock - when pressed, all requests are rejected until F9 is long-pressed (2 seconds) again
- **Web Frontend**: Interactive web interface for defining tasks and AI-powered automation

## Architecture

- **FastAPI Server** (`main.py`): Runs as regular user, provides REST API endpoints
- **Privileged Worker** (`privileged_worker.py`): Runs as subprocess with elevated privileges, handles actual screenshot/input operations
- Communication between them via stdin/stdout using JSON

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make the privileged worker executable:
```bash
chmod +x privileged_worker.py
```

3. Configure sudo (optional, if you want passwordless sudo):
   - Add to `/etc/sudoers` (use `visudo`):
   ```
   your_username ALL=(ALL) NOPASSWD: /usr/bin/python3 /path/to/privileged_worker.py
   ```
   - Or run the server with sudo privileges already

4. Set up AI API key (required for web frontend):
   - For OpenAI:
     ```bash
     export OPENAI_API_KEY="your-api-key-here"
     ```
   - For Google Gemini:
     ```bash
     export GEMINI_API_KEY="your-api-key-here"
     ```
   You can set up one or both. The web interface allows you to choose which provider to use.

## Usage

### Start the Server

```bash
python3 main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

### Web Frontend

Open your browser and navigate to `http://localhost:8000` to access the web interface.

**Using the Web Frontend:**

1. **Select AI Model**: Choose between OpenAI (GPT-4 Vision) or Google Gemini, and select the specific model
2. **Define Task**: Enter a description of what you want the AI to accomplish
3. **Select Area**: Click "Capture Screen" and then click and drag to select the area of interest
4. **Start Task**: Click "Start Task" to begin AI-powered automation
5. **Monitor Progress**: Watch the conversation log as the AI analyzes screenshots and performs actions
6. **Handle Issues**: If the AI needs help or an action is rejected, you'll be prompted to assist

The frontend supports both OpenAI's vision models (GPT-4 Vision, GPT-4o) and Google's Gemini models (Gemini 1.5 Pro, Gemini 1.5 Flash) to analyze screenshots and determine the next action. Actions are executed automatically, and if any action is rejected by the backend (e.g., due to safety mode), the system will pause and ask for your help.

### API Endpoints

#### Status
- `GET /status` - Get current status including safety mode state

#### Screenshot
- `POST /screenshot` - Take a screenshot (returns base64 encoded PNG)

#### Mouse Control
- `POST /mouse/move` - Move mouse to coordinates
  ```json
  {"x": 100, "y": 200}
  ```
- `POST /mouse/click` - Click at coordinates
  ```json
  {"x": 100, "y": 200, "button": "left"}
  ```
- `POST /mouse/drag_drop` - Drag from one point to another
  ```json
  {"x": 100, "y": 200, "x_drop": 300, "y_drop": 400, "button": "left"}
  ```
- `POST /mouse/button/down` - Press mouse button down
  ```json
  {"button": "left"}
  ```
- `POST /mouse/button/up` - Release mouse button
  ```json
  {"button": "left"}
  ```

#### Keyboard Control
- `POST /keyboard/type` - Type a string
  ```json
  {"text": "Hello World"}
  ```
- `POST /keyboard/press` - Press a key
  ```json
  {"key": "a"}
  ```
  Supported special keys: `page_up`, `page_down`, `home`, `end`, `up`, `down`, `left`, `right`, `enter`, `tab`, `escape`, `backspace`, `delete`, `space`
- `POST /keyboard/page_up` - Press Page Up key
- `POST /keyboard/page_down` - Press Page Down key

### Safety Mechanism

- **F9 Short Press**: Activates safety mode - all requests are rejected
- **F9 Long Press (2 seconds)**: Deactivates safety mode - requests are accepted again

The safety mode status can be checked via the `/status` endpoint.

### Example Usage

```bash
# Get status
curl http://localhost:8000/status

# Take screenshot
curl -X POST http://localhost:8000/screenshot

# Click at (100, 200)
curl -X POST http://localhost:8000/mouse/click \
  -H "Content-Type: application/json" \
  -d '{"x": 100, "y": 200, "button": "left"}'

# Type text
curl -X POST http://localhost:8000/keyboard/type \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World"}'

# Press Page Down
curl -X POST http://localhost:8000/keyboard/page_down
```

## Security Considerations

- The privileged worker requires elevated privileges to access input devices
- The FastAPI server should be protected with authentication in production
- Consider using HTTPS in production
- The F9 safety mechanism provides a local physical safety override

## Troubleshooting

1. **Permission denied errors**: Ensure the privileged worker can access input devices. You may need to:
   - Run with sudo
   - Add your user to the `input` group: `sudo usermod -a -G input $USER`
   - Configure X11 permissions

2. **Worker process fails to start**: Check that Python and all dependencies are installed, and that the script path is correct.

3. **Screenshot not working**: Ensure you have X11 display access (set `DISPLAY` environment variable if needed).

## License

This project is provided as-is for educational and development purposes.

