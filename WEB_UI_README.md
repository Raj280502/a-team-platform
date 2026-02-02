# AI Code Factory - Web IDE

A web-based IDE for the AI Code Factory with integrated code editor and terminal.

## Features

✨ **Monaco Editor** - Full-featured code editor with syntax highlighting
🖥️ **Integrated Terminal** - Execute commands and see output in real-time
🤖 **AI Code Generation** - Generate full-stack apps from natural language
🔄 **Real-time Updates** - See code being generated live
💾 **Auto-save** - Press Ctrl+S to save changes
🐛 **Error Feedback** - Errors are automatically fed back to AI for fixes

## Quick Start

### 1. Install Dependencies

```bash
pip install flask flask-cors flask-socketio python-socketio
```

### 2. Start the Web Server

```bash
python web_ui.py
```

### 3. Open in Browser

Navigate to: **http://localhost:8080**

## Usage

1. **Enter a Prompt**: Type your app description (e.g., "todo app", "calculator")
2. **Click Generate**: The AI will start generating your app
3. **Watch Progress**: See files being created in real-time
4. **Edit Code**: Click any file to open it in the editor
5. **Run Commands**: Use the terminal to test, install packages, etc.
6. **Save Changes**: Press Ctrl+S or files auto-save on blur

## Architecture

```
web_ui.py           → Flask backend with WebSocket support
templates/
  index.html        → Full IDE interface with Monaco + xterm.js
app/
  main.py           → Generation pipeline (callable by web UI)
  graph/            → LangGraph workflow
  agents/           → AI agents (strategist, architect, coder, etc.)
```

## Keyboard Shortcuts

- `Ctrl+S` - Save current file
- `Ctrl+Enter` - Execute command in terminal
- `Ctrl+\`` - Focus terminal

## API Endpoints

### HTTP REST

- `POST /api/generate` - Start project generation
- `GET /api/status` - Get generation status
- `GET /api/files/<path>` - Get file content
- `PUT /api/files/<path>` - Save file content
- `GET /api/project/files` - List all project files

### WebSocket Events

- `execute_command` - Execute terminal command
- `terminal_output` - Stream terminal output
- `generation_status` - Generation status updates
- `project_ready` - Project generation completed

## Technology Stack

### Frontend
- **Monaco Editor** - VS Code's editor component
- **Xterm.js** - Full terminal emulator
- **Socket.IO** - Real-time communication
- **Vanilla JS** - No framework bloat

### Backend
- **Flask** - Lightweight web framework
- **Flask-SocketIO** - WebSocket support
- **LangGraph** - AI workflow orchestration
- **Hugging Face** - LLM inference

## Benefits Over CLI

✅ **Visual Feedback** - See code as it's generated
✅ **Easy Editing** - No need to switch to external editor
✅ **Integrated Terminal** - Test immediately in same window
✅ **File Tree** - Quick navigation
✅ **Syntax Highlighting** - Better readability
✅ **Error Context** - See exactly where errors occur

## Future Enhancements

- [ ] Multi-file editing (tabs)
- [ ] File search and replace
- [ ] Git integration
- [ ] Collaborative editing
- [ ] Theme customization
- [ ] Debugger integration
- [ ] Package manager UI
- [ ] Deployment wizard

## Troubleshooting

**Port 8080 already in use?**
```bash
# Change port in web_ui.py, line: socketio.run(app, port=8080)
```

**Terminal not working?**
```bash
# Make sure Socket.IO is installed:
pip install python-socketio flask-socketio
```

**Editor not loading?**
```bash
# Check browser console for CDN issues
# Try refreshing the page
```

## License

MIT License - See main project LICENSE file
