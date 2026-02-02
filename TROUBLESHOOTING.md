# Web UI Troubleshooting Guide

## Quick Diagnostics

### 1. Test Server Health
Open in browser: `http://localhost:8080/health`

Expected response:
```json
{
  "status": "ok",
  "message": "AI Code Factory Web UI is running",
  "current_project": null
}
```

### 2. Test Imports
Open in browser: `http://localhost:8080/api/test`

Expected response:
```json
{
  "status": "ok",
  "message": "Imports working"
}
```

If you get an error, the `app` module isn't importable.

### 3. Check Browser Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Click "Generate"
4. Look for error messages

Common errors:
- `Socket.IO connection failed` → Check if server is running
- `Failed to fetch` → CORS issue or server down
- `Import error` → Missing dependencies or wrong Python path

### 4. Check Terminal Output
When you click Generate, you should see in the server terminal:
```
🚀 Starting generation for: your prompt
📡 Status emitted: running
🔄 Calling run_pipeline...
```

If you see `❌ Import error`, run:
```bash
pip install langchain langgraph langchain-community
```

## Common Issues

### Issue: Nothing happens when I click Generate

**Check:**
1. Open browser console (F12) → Look for errors
2. Check server terminal → Any Python errors?
3. Visit `/api/test` → Does it work?

**Fix:**
```bash
# Restart server
Ctrl+C
python web_ui.py
```

### Issue: "Import error: No module named 'app'"

**Fix:**
```bash
# Make sure you're in the project root
cd C:\A_Team_cursor

# Run server from root directory
python web_ui.py
```

### Issue: Socket.IO not connecting

**Check browser console:**
```
Failed to load resource: net::ERR_CONNECTION_REFUSED
```

**Fix:**
```bash
pip install flask-socketio python-socketio
```

### Issue: Generation starts but fails immediately

**Check server logs for:**
- `KeyError` → Missing state field
- `ImportError` → Missing dependency
- `FileNotFoundError` → Wrong working directory

**Fix:**
Run from project root and check all dependencies:
```bash
pip install -r requirements.txt
```

## Step-by-Step Debug

1. **Restart the server** (Ctrl+C, then `python web_ui.py`)
2. **Open browser** at `http://localhost:8080`
3. **Open DevTools** (F12)
4. **Enter prompt** "test app"
5. **Click Generate**
6. **Check both**:
   - Browser console for frontend errors
   - Terminal for backend errors

## Getting Help

If none of this works, provide:
1. Browser console errors (F12 → Console tab)
2. Server terminal output
3. Output of: `pip list | findstr flask`
4. Output of: `python --version`

## Expected Flow

```
User clicks Generate
    ↓
Browser → POST /api/generate
    ↓
Server receives request
    ↓
Starts background thread
    ↓
Imports app.main.run_pipeline
    ↓
Calls run_pipeline(prompt)
    ↓
LangGraph executes
    ↓
Emits status updates via Socket.IO
    ↓
Browser shows progress
    ↓
Generation completes
    ↓
Files appear in sidebar
```

## Quick Fixes

**Can't import app module:**
```python
# Add this to web_ui.py (already added):
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

**Socket.IO not working:**
```bash
pip uninstall flask-socketio python-socketio
pip install flask-socketio==5.3.5 python-socketio==5.10.0
```

**Port already in use:**
Change port in `web_ui.py`:
```python
socketio.run(app, host='0.0.0.0', port=8081, debug=True)
```
