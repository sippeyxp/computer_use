// Configuration
const API_BASE = 'http://localhost:8000';

// State
let state = {
    taskDescription: '',
    cropArea: null,
    conversationHistory: [],
    isRunning: false,
    isPaused: false,
    currentScreenshot: null,
    fullScreenshot: null,
    aiProvider: 'openai',
    aiModel: 'gpt-4-vision-preview',
    openaiApiKey: '',
    geminiApiKey: '',
    initialPrompt: '',
    perStepPrompt: '',
    showRawOutput: false,
    thinkingBudget: '',
    mediaResolution: ''
};

// DOM Elements
const setupPhase = document.getElementById('setupPhase');
const conversationPhase = document.getElementById('conversationPhase');
const taskDescription = document.getElementById('taskDescription');
const captureBtn = document.getElementById('captureBtn');
const screenshotContainer = document.getElementById('screenshotContainer');
const screenshotCanvas = document.getElementById('screenshotCanvas');
const cropOverlay = document.getElementById('cropOverlay');
const confirmAreaBtn = document.getElementById('confirmAreaBtn');
const startTaskBtn = document.getElementById('startTaskBtn');
const conversationLog = document.getElementById('conversationLog');
const pauseBtn = document.getElementById('pauseBtn');
const stopBtn = document.getElementById('stopBtn');
const helpModal = document.getElementById('helpModal');
const helpMessage = document.getElementById('helpMessage');
const helpDetails = document.getElementById('helpDetails');
const resumeBtn = document.getElementById('resumeBtn');
const cancelTaskBtn = document.getElementById('cancelTaskBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const modelNameInput = document.getElementById('modelNameInput');
const openaiKeyInput = document.getElementById('openaiKeyInput');
const geminiKeyInput = document.getElementById('geminiKeyInput');
const initialPromptInput = document.getElementById('initialPromptInput');
const perStepPromptInput = document.getElementById('perStepPromptInput');
const togglePowerUserBtn = document.getElementById('togglePowerUserBtn');
const powerUserOptions = document.getElementById('powerUserOptions');

// Crop selection state
let isSelecting = false;
let startX = 0, startY = 0;
let currentX = 0, currentY = 0;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSavedSettings();
    setupEventListeners();
    updateStatus('ready', 'Ready');
});

function loadSavedSettings() {
    // Load from localStorage
    const savedProvider = localStorage.getItem('aiProvider');
    const savedModel = localStorage.getItem('aiModel');
    const savedOpenaiKey = localStorage.getItem('openaiApiKey');
    const savedGeminiKey = localStorage.getItem('geminiApiKey');
    
    if (savedProvider) {
        state.aiProvider = savedProvider;
        const radio = document.querySelector(`input[name="aiProvider"][value="${savedProvider}"]`);
        if (radio) {
            radio.checked = true;
        }
    }
    
    if (savedModel) {
        state.aiModel = savedModel;
        modelNameInput.value = savedModel;
    } else {
        // Set default model if none saved
        if (state.aiProvider === 'openai') {
            state.aiModel = 'gpt-4-vision-preview';
            modelNameInput.value = state.aiModel;
        } else if (state.aiProvider === 'gemini') {
            state.aiModel = 'gemini-1.5-pro';
            modelNameInput.value = state.aiModel;
        }
    }
    
    if (savedOpenaiKey) {
        state.openaiApiKey = savedOpenaiKey;
        openaiKeyInput.value = savedOpenaiKey;
    }
    
    if (savedGeminiKey) {
        state.geminiApiKey = savedGeminiKey;
        geminiKeyInput.value = savedGeminiKey;
    }
    
    const savedInitialPrompt = localStorage.getItem('initialPrompt');
    const savedPerStepPrompt = localStorage.getItem('perStepPrompt');
    
    if (savedInitialPrompt) {
        state.initialPrompt = savedInitialPrompt;
        initialPromptInput.value = savedInitialPrompt;
    }
    
    if (savedPerStepPrompt) {
        state.perStepPrompt = savedPerStepPrompt;
        perStepPromptInput.value = savedPerStepPrompt;
    }
    
    const savedShowRawOutput = localStorage.getItem('showRawOutput');
    if (savedShowRawOutput === 'true') {
        state.showRawOutput = true;
        if (showRawOutputCheckbox) {
            showRawOutputCheckbox.checked = true;
        }
    }
    
    const savedThinkingBudget = localStorage.getItem('thinkingBudget');
    if (savedThinkingBudget) {
        state.thinkingBudget = savedThinkingBudget;
        if (thinkingBudgetInput) {
            thinkingBudgetInput.value = savedThinkingBudget;
        }
    }
    
    const savedMediaResolution = localStorage.getItem('mediaResolution');
    if (savedMediaResolution) {
        state.mediaResolution = savedMediaResolution;
        if (mediaResolutionSelect) {
            mediaResolutionSelect.value = savedMediaResolution;
        }
    }
}

function saveSettings() {
    localStorage.setItem('aiProvider', state.aiProvider);
    localStorage.setItem('aiModel', state.aiModel);
    if (state.openaiApiKey) {
        localStorage.setItem('openaiApiKey', state.openaiApiKey);
    }
    if (state.geminiApiKey) {
        localStorage.setItem('geminiApiKey', state.geminiApiKey);
    }
    if (state.initialPrompt) {
        localStorage.setItem('initialPrompt', state.initialPrompt);
    }
    if (state.perStepPrompt) {
        localStorage.setItem('perStepPrompt', state.perStepPrompt);
    }
    localStorage.setItem('showRawOutput', state.showRawOutput.toString());
    if (state.thinkingBudget) {
        localStorage.setItem('thinkingBudget', state.thinkingBudget);
    }
    if (state.mediaResolution) {
        localStorage.setItem('mediaResolution', state.mediaResolution);
    }
}

function setupEventListeners() {
    taskDescription.addEventListener('input', () => {
        state.taskDescription = taskDescription.value;
        updateStartButton();
    });

    // AI Provider selection
    const providerRadios = document.querySelectorAll('input[name="aiProvider"]');
    providerRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            state.aiProvider = e.target.value;
            // Set default model name based on provider
            if (state.aiProvider === 'openai' && !modelNameInput.value) {
                state.aiModel = 'gpt-4-vision-preview';
                modelNameInput.value = state.aiModel;
            } else if (state.aiProvider === 'gemini' && !modelNameInput.value) {
                state.aiModel = 'gemini-1.5-pro';
                modelNameInput.value = state.aiModel;
            }
            saveSettings();
        });
    });

    // Model name input
    modelNameInput.addEventListener('input', (e) => {
        state.aiModel = e.target.value;
        saveSettings();
    });

    // API key inputs
    openaiKeyInput.addEventListener('input', (e) => {
        state.openaiApiKey = e.target.value;
        saveSettings();
    });

    geminiKeyInput.addEventListener('input', (e) => {
        state.geminiApiKey = e.target.value;
        saveSettings();
    });

    // Prompt inputs
    initialPromptInput.addEventListener('input', (e) => {
        state.initialPrompt = e.target.value;
        saveSettings();
    });

    perStepPromptInput.addEventListener('input', (e) => {
        state.perStepPrompt = e.target.value;
        saveSettings();
    });

    // Show raw output checkbox
    if (showRawOutputCheckbox) {
        showRawOutputCheckbox.addEventListener('change', (e) => {
            state.showRawOutput = e.target.checked;
            saveSettings();
        });
    }

    // Thinking budget input
    if (thinkingBudgetInput) {
        thinkingBudgetInput.addEventListener('input', (e) => {
            state.thinkingBudget = e.target.value;
            saveSettings();
        });
    }

    // Media resolution select
    if (mediaResolutionSelect) {
        mediaResolutionSelect.addEventListener('change', (e) => {
            state.mediaResolution = e.target.value;
            saveSettings();
        });
    }

    // Toggle power user options
    togglePowerUserBtn.addEventListener('click', () => {
        const isVisible = powerUserOptions.style.display !== 'none';
        powerUserOptions.style.display = isVisible ? 'none' : 'block';
        togglePowerUserBtn.textContent = isVisible ? 'Show' : 'Hide';
    });

    captureBtn.addEventListener('click', captureScreenshot);
    confirmAreaBtn.addEventListener('click', confirmCropArea);
    startTaskBtn.addEventListener('click', startTask);
    pauseBtn.addEventListener('click', pauseTask);
    stopBtn.addEventListener('click', stopTask);
    resumeBtn.addEventListener('click', resumeTask);
    cancelTaskBtn.addEventListener('click', cancelTask);

    // Crop selection
    screenshotCanvas.addEventListener('mousedown', startCropSelection);
    screenshotCanvas.addEventListener('mousemove', updateCropSelection);
    screenshotCanvas.addEventListener('mouseup', endCropSelection);
    screenshotCanvas.addEventListener('mouseleave', endCropSelection);
}

// Removed updateModelOptions - now using text input

async function captureScreenshot() {
    try {
        updateStatus('loading', 'Capturing screenshot...');
        const response = await fetch(`${API_BASE}/screenshot`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            state.fullScreenshot = data;
            displayScreenshot(data.image, data.width, data.height);
            screenshotContainer.style.display = 'block';
            updateStatus('ready', 'Select area of interest');
        } else {
            alert('Failed to capture screenshot: ' + data.error);
            updateStatus('error', 'Screenshot failed');
        }
    } catch (error) {
        alert('Error capturing screenshot: ' + error.message);
        updateStatus('error', 'Screenshot error');
    }
}

function displayScreenshot(imageData, width, height) {
    const img = new Image();
    img.onload = () => {
        screenshotCanvas.width = Math.min(width, 1200);
        screenshotCanvas.height = (screenshotCanvas.width / width) * height;
        const ctx = screenshotCanvas.getContext('2d');
        ctx.drawImage(img, 0, 0, screenshotCanvas.width, screenshotCanvas.height);
        state.currentScreenshot = {
            image: imageData,
            width: width,
            height: height,
            displayWidth: screenshotCanvas.width,
            displayHeight: screenshotCanvas.height,
            scaleX: width / screenshotCanvas.width,
            scaleY: height / screenshotCanvas.height
        };
    };
    img.src = 'data:image/png;base64,' + imageData;
}

function startCropSelection(e) {
    isSelecting = true;
    const rect = screenshotCanvas.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;
    currentX = startX;
    currentY = startY;
    cropOverlay.style.display = 'block';
    updateCropOverlay();
}

function updateCropSelection(e) {
    if (!isSelecting) return;
    const rect = screenshotCanvas.getBoundingClientRect();
    currentX = e.clientX - rect.left;
    currentY = e.clientY - rect.top;
    updateCropOverlay();
}

function endCropSelection() {
    if (isSelecting) {
        isSelecting = false;
        if (Math.abs(currentX - startX) > 10 && Math.abs(currentY - startY) > 10) {
            confirmAreaBtn.style.display = 'block';
        }
    }
}

function updateCropOverlay() {
    const x = Math.min(startX, currentX);
    const y = Math.min(startY, currentY);
    const width = Math.abs(currentX - startX);
    const height = Math.abs(currentY - startY);
    
    cropOverlay.style.left = x + 'px';
    cropOverlay.style.top = y + 'px';
    cropOverlay.style.width = width + 'px';
    cropOverlay.style.height = height + 'px';
}

function confirmCropArea() {
    const x = Math.min(startX, currentX);
    const y = Math.min(startY, currentY);
    const width = Math.abs(currentX - startX);
    const height = Math.abs(currentY - startY);
    
    // Convert display coordinates to actual screenshot coordinates
    state.cropArea = {
        x: Math.round(x * state.currentScreenshot.scaleX),
        y: Math.round(y * state.currentScreenshot.scaleY),
        width: Math.round(width * state.currentScreenshot.scaleX),
        height: Math.round(height * state.currentScreenshot.scaleY)
    };
    
    updateStartButton();
    addMessage('user', 'Area selected', `Selected area: ${state.cropArea.width}x${state.cropArea.height} at (${state.cropArea.x}, ${state.cropArea.y})`);
}

function updateStartButton() {
    startTaskBtn.disabled = !state.taskDescription.trim() || !state.cropArea;
}

async function startTask() {
    if (!state.taskDescription.trim() || !state.cropArea) {
        alert('Please define a task and select an area of interest');
        return;
    }
    
    setupPhase.classList.remove('active');
    conversationPhase.classList.add('active');
    state.isRunning = true;
    state.isPaused = false;
    state.conversationHistory = [];
    
    updateStatus('active', 'Task running');
    
    // Send initial task description with custom prompt if provided
    addMessage('user', 'Task', state.taskDescription);
    
    // Use custom initial prompt or default
    const defaultInitialPrompt = `Task: {task}\n\nI will provide screenshots of the selected area. Please analyze them and provide actions to complete the task. Actions should be in JSON format: {"action": "click", "y": 100, "button": "left"} or {"action": "type", "text": "hello"} or {"action": "key_press", "key": "enter"} or {"action": "drag_drop", "x": 100, "y": 200, "x_drop": 300, "y_drop": 400, "button": "left"} or {"action": "ask_human", "message": "I need help with..."}`;
    
    const initialPrompt = state.initialPrompt || defaultInitialPrompt;
    const initialPromptText = initialPrompt.replace('{task}', state.taskDescription);
    
    state.conversationHistory.push({
        role: 'user',
        content: initialPromptText
    });
    
    // Start conversation loop
    await conversationLoop();
}

async function conversationLoop() {
    while (state.isRunning && !state.isPaused) {
        try {
            // Get cropped screenshot
            updateStatus('active', 'Capturing screenshot...');
            const croppedScreenshot = await getCroppedScreenshot();
            
            if (!croppedScreenshot.success) {
                addMessage('error', 'Screenshot Error', croppedScreenshot.error);
                await askForHelp('Failed to capture screenshot: ' + croppedScreenshot.error);
                break;
            }
            
            // Add screenshot to conversation
            addMessage('ai', 'Screenshot', 'Analyzing current state...', croppedScreenshot.image);
            
            // Get action from AI
            updateStatus('active', 'Getting AI action...');
            const action = await getAIAction(croppedScreenshot.image);
            
            if (!action) {
                await askForHelp('AI did not return a valid action');
                break;
            }
            
            // Show raw output if enabled
            if (state.showRawOutput && action._rawOutput) {
                addMessage('ai', 'Raw Model Output', action._rawOutput);
            }
            
            // Execute action (create a copy without _rawOutput for display)
            const actionForDisplay = { ...action };
            delete actionForDisplay._rawOutput;
            addMessage('action', 'Executing Action', JSON.stringify(actionForDisplay, null, 2));
            const result = await executeAction(action);
            
            // Handle ask_human action (from executeAction or directly)
            if (result.action === 'ask_human' || action.action === 'ask_human') {
                await askForHelp(result.message || action.message || 'AI needs your assistance');
                break;
            }
            
            if (!result.success) {
                // Action rejected - ask for help (don't add to history since it failed)
                addMessage('error', 'Action Rejected', result.error || 'Action was rejected by the backend');
                await askForHelp(`Action was rejected: ${result.error || 'Unknown error'}. Action: ${JSON.stringify(action)}`);
                break;
            }
            
            // Action succeeded - add to conversation history for context
            state.conversationHistory.push({
                role: 'assistant',
                content: `I performed action: ${JSON.stringify(action)}. Result: success`
            });
            
            // Small delay before next iteration
            await sleep(1000);
            
        } catch (error) {
            addMessage('error', 'Error', error.message);
            await askForHelp('An error occurred: ' + error.message);
            break;
        }
    }
}

async function getCroppedScreenshot() {
    try {
        const response = await fetch(`${API_BASE}/screenshot/crop`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state.cropArea)
        });
        return await response.json();
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function getAIAction(screenshotBase64) {
    try {
        // Use custom per-step prompt or default
        // Different prompts for Gemini vs OpenAI
        let defaultPerStepPrompt;
        if (state.aiProvider === 'gemini') {
            defaultPerStepPrompt = 'Your actions are:\n\n* Page up, output {"action": "page up"}\n* Page down, output {"action": "page down"}\n* Click, output point in [y, x], normalized to 0-1000, output {"action": "click", "point": [y, x]}\n* Drag drop, output point of drag start and drop in [y, x], normalized to 0-1000, output {"action": "drag_drop", "drag_point": [y, x], "drop_point": [y, x]}\n* Ask for human to help, {"action": "ask_human", "message": "..."}\n* Type a string. Make sure you clicked the proper input box to set focus first. {"action": "type", "content": "string to type"}\n\nAnalyze this screenshot and provide the next action to complete the task. Respond with ONLY a JSON object.';
        } else {
            defaultPerStepPrompt = 'Analyze this screenshot and provide the next action to complete the task. Respond with ONLY a JSON object in this format: {"action": "click", "x": 100, "y": 200} or {"action": "type", "text": "hello"} or {"action": "key_press", "key": "enter"} or {"action": "drag_drop", "x": 100, "y": 200, "x_drop": 300, "y_drop": 400} or {"action": "ask_human", "message": "I need help..."}';
        }
        
        const perStepPrompt = state.perStepPrompt || defaultPerStepPrompt;
        const perStepPromptText = perStepPrompt.replace('{task}', state.taskDescription);
        
        const messages = [
            ...state.conversationHistory,
            {
                role: 'user',
                content: [
                    {
                        type: 'text',
                        text: perStepPromptText
                    },
                    {
                        type: 'image_url',
                        image_url: {
                            url: `data:image/png;base64,${screenshotBase64}`
                        }
                    }
                ]
            }
        ];
        
        // Prepare request body with API keys if provided
        const requestBody = {
            provider: state.aiProvider,
            model: state.aiModel,
            messages: messages,
            max_tokens: 50000,
            temperature: 1.0
        };
        
        // Add API keys if provided (frontend takes precedence over env vars)
        if (state.aiProvider === 'openai' && state.openaiApiKey) {
            requestBody.api_key = state.openaiApiKey;
        } else if (state.aiProvider === 'gemini' && state.geminiApiKey) {
            requestBody.api_key = state.geminiApiKey;
        }
        
        // Add thinking budget for Gemini
        if (state.aiProvider === 'gemini' && state.thinkingBudget) {
            requestBody.thinking_budget = parseInt(state.thinkingBudget, 10);
        }
        
        // Add media resolution for OpenAI (add detail to image_url)
        if (state.mediaResolution && state.aiProvider === 'openai') {
            // Apply media resolution to image URLs in messages
            const detailMap = {
                'low': 'low',
                'medium': 'auto',
                'high': 'high'
            };
            const detail = detailMap[state.mediaResolution] || 'auto';
            
            // Update the last message's image_url to include detail
            if (messages.length > 0) {
                const lastMsg = messages[messages.length - 1];
                if (lastMsg.content && Array.isArray(lastMsg.content)) {
                    lastMsg.content.forEach(part => {
                        if (part.type === 'image_url' && part.image_url) {
                            if (!part.image_url.detail) {
                                part.image_url.detail = detail;
                            }
                        }
                    });
                }
            }
        }
        
        const response = await fetch(`${API_BASE}/ai/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'AI API request failed');
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error.message);
        }
        
        const content = data.choices[0].message.content.trim();
        
        // Store raw output if enabled
        let rawOutput = content;
        
        // Try to extract JSON from response
        let jsonMatch = content.match(/\{[\s\S]*\}/);
        let parsedAction = null;
        
        if (jsonMatch) {
            parsedAction = JSON.parse(jsonMatch[0]);
        } else {
            // If no JSON found, try parsing the whole content
            parsedAction = JSON.parse(content);
        }
        
        // Attach raw output to the action object for display
        if (parsedAction) {
            parsedAction._rawOutput = rawOutput;
        }
        
        return parsedAction;
        
    } catch (error) {
        console.error('AI API error:', error);
        return null;
    }
}

async function executeAction(action) {
    try {
        // Map AI action format to backend format
        let actionType = action.action;
        let parameters = {};
        
        // Handle Gemini format (normalized coordinates)
        if (state.aiProvider === 'gemini') {
            if (actionType === 'click' && action.point) {
                // Convert normalized [y, x] (0-1000) to actual pixel coordinates
                const [normalizedY, normalizedX] = action.point;
                const actualX = Math.round((normalizedX / 1000) * state.cropArea.width) + state.cropArea.x;
                const actualY = Math.round((normalizedY / 1000) * state.cropArea.height) + state.cropArea.y;
                actionType = 'click';
                parameters = { x: actualX, y: actualY, button: 'left' };
            } else if (actionType === 'drag_drop' && action.drag_point && action.drop_point) {
                // Convert normalized [y, x] coordinates to actual pixel coordinates
                const [dragY, dragX] = action.drag_point;
                const [dropY, dropX] = action.drop_point;
                const actualDragX = Math.round((dragX / 1000) * state.cropArea.width) + state.cropArea.x;
                const actualDragY = Math.round((dragY / 1000) * state.cropArea.height) + state.cropArea.y;
                const actualDropX = Math.round((dropX / 1000) * state.cropArea.width) + state.cropArea.x;
                const actualDropY = Math.round((dropY / 1000) * state.cropArea.height) + state.cropArea.y;
                actionType = 'drag_drop';
                parameters = {
                    x: actualDragX,
                    y: actualDragY,
                    x_drop: actualDropX,
                    y_drop: actualDropY,
                    button: 'left'
                };
            } else if (actionType === 'page up') {
                actionType = 'key_press';
                parameters = { key: 'page_up' };
            } else if (actionType === 'page down') {
                actionType = 'key_press';
                parameters = { key: 'page_down' };
            } else if (actionType === 'type' && action.content) {
                actionType = 'type';
                parameters = { text: action.content };
            } else if (actionType === 'ask_human') {
                // This will be handled in the conversation loop
                return { success: true, action: 'ask_human', message: action.message || 'AI needs your assistance' };
            } else {
                return { success: false, error: `Unknown Gemini action type: ${actionType}` };
            }
        } else {
            // Handle OpenAI format (pixel coordinates)
            if (actionType === 'click') {
                actionType = 'click';
                parameters = { x: action.x, y: action.y, button: action.button || 'left' };
            } else if (actionType === 'type') {
                actionType = 'type';
                parameters = { text: action.text || action.content };
            } else if (actionType === 'key_press') {
                actionType = 'key_press';
                parameters = { key: action.key };
            } else if (actionType === 'drag_drop') {
                actionType = 'drag_drop';
                parameters = {
                    x: action.x,
                    y: action.y,
                    x_drop: action.x_drop,
                    y_drop: action.y_drop,
                    button: action.button || 'left'
                };
            } else if (actionType === 'move') {
                actionType = 'move';
                parameters = { x: action.x, y: action.y };
            } else {
                return { success: false, error: `Unknown action type: ${actionType}` };
            }
        }
        
        const response = await fetch(`${API_BASE}/execute_action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action_type: actionType,
                parameters: parameters
            })
        });
        
        return await response.json();
        
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function askForHelp(message, details = null) {
    state.isPaused = true;
    helpMessage.textContent = message;
    
    if (details) {
        helpDetails.textContent = JSON.stringify(details, null, 2);
        helpDetails.style.display = 'block';
    } else {
        helpDetails.style.display = 'none';
    }
    
    helpModal.style.display = 'flex';
    updateStatus('paused', 'Waiting for help');
}

function resumeTask() {
    helpModal.style.display = 'none';
    state.isPaused = false;
    updateStatus('active', 'Task running');
    conversationLoop();
}

function pauseTask() {
    state.isPaused = true;
    updateStatus('paused', 'Paused');
}

function stopTask() {
    state.isRunning = false;
    state.isPaused = false;
    conversationPhase.classList.remove('active');
    setupPhase.classList.add('active');
    updateStatus('ready', 'Ready');
    addMessage('user', 'Task Stopped', 'Task execution stopped by user');
}

function cancelTask() {
    stopTask();
    helpModal.style.display = 'none';
}

function addMessage(type, title, content, image = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const header = document.createElement('div');
    header.className = 'message-header';
    header.textContent = title;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    if (image) {
        const img = document.createElement('img');
        img.src = 'data:image/png;base64,' + image;
        img.className = 'screenshot-preview';
        messageContent.appendChild(img);
    }
    
    if (typeof content === 'string' && content.length > 100) {
        const pre = document.createElement('pre');
        pre.textContent = content;
        messageContent.appendChild(pre);
    } else {
        messageContent.appendChild(document.createTextNode(content));
    }
    
    messageDiv.appendChild(header);
    messageDiv.appendChild(messageContent);
    conversationLog.appendChild(messageDiv);
    conversationLog.scrollTop = conversationLog.scrollHeight;
}

function updateStatus(status, text) {
    statusText.textContent = text;
    statusDot.className = 'status-dot ' + status;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

