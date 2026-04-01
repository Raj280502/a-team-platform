# 🏗️ AI Code Factory — Implementation Plan

> Detailed technical architecture and implementation blueprint for the A-Team AI Code Factory platform.

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                             │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  Chat Panel  │  │  Code Panel  │  │Preview Panel │  │ Stage Pages│  │
│  │  (ChatPanel) │  │  (Monaco)    │  │  (iframe)    │  │ (5 SDLC)   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘  │
│         │                 │                 │                 │          │
│         └─────────────────┼─────────────────┼─────────────────┘          │
│                           │                 │                            │
│  React 19 + Vite ─────────┼─────────────────┼──── SSE + REST + WS       │
└───────────────────────────┼─────────────────┼────────────────────────────┘
                            │                 │
                     ┌──────┴─────────────────┴───────┐
                     │     FLASK WEB SERVER (8080)     │
                     │         web_ui.py               │
                     │                                 │
                     │  ┌─────────┐  ┌──────────────┐  │
                     │  │REST API │  │  Socket.IO    │  │
                     │  │18 routes│  │  bidirectional│  │
                     │  └────┬────┘  └──────┬───────┘  │
                     └───────┼──────────────┼──────────┘
                             │              │
                     ┌───────┴──────────────┴──────────┐
                     │    PIPELINE ORCHESTRATION LAYER  │
                     │          app/main.py             │
                     │                                  │
                     │   LangGraph State Machine        │
                     │   ┌──────────────────────────┐   │
                     │   │  ProjectState (TypedDict) │   │
                     │   │  - Shared pipeline memory │   │
                     │   │  - 25+ typed fields       │   │
                     │   └──────────────────────────┘   │
                     └──────────────┬───────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
    ┌─────┴──────┐          ┌──────┴───────┐          ┌──────┴───────┐
    │   SDLC     │          │   CODE GEN   │          │   CHAT       │
    │  PIPELINE  │          │   PIPELINE   │          │  PIPELINE    │
    │ (5 stages) │          │ (7+ nodes)   │          │ (3 nodes)    │
    └────────────┘          └──────────────┘          └──────────────┘
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    │
                     ┌──────────────┴───────────────────┐
                     │     LLM PROVIDER LAYER            │
                     │       app/core/llm.py             │
                     │                                   │
                     │  ┌────────────────────────────┐   │
                     │  │    FallbackLLM Wrapper      │   │
                     │  │  Primary: Groq (70B)        │   │
                     │  │  Fallback: Google Gemini    │   │
                     │  │  + Rate limit detection     │   │
                     │  │  + Auto-retry with backoff  │   │
                     │  └────────────────────────────┘   │
                     └──────────────┬───────────────────┘
                                    │
                     ┌──────────────┴───────────────────┐
                     │     PERSISTENCE LAYER             │
                     │     app/core/database.py          │
                     │                                   │
                     │  SQLite (projects.db)              │
                     │  ┌────────────┐ ┌──────────────┐  │
                     │  │  projects   │ │ sdlc_stages  │  │
                     │  │  files      │ │ versions     │  │
                     │  │  messages   │ │              │  │
                     │  └────────────┘ └──────────────┘  │
                     └───────────────────────────────────┘
```

---

## 2. Pipeline Architecture Detail

### 2.1 Code Generation Pipeline

The core pipeline is implemented as a **LangGraph StateGraph** with conditional edges:

```
Entry Point
    │
    ▼
┌─────────────────────┐
│   STRATEGIST NODE    │  ← Extracts: project_goal, features, pages, data_models,
│   (70B model)        │     API endpoints, UI style, technical constraints
│   Output: Pydantic   │
└──────────┬──────────┘
           │ project_scope
           ▼
┌─────────────────────┐
│   ARCHITECT NODE     │  ← Designs: backend routes, frontend components,
│   (70B model)        │     file structure, data flow
│   Output: Pydantic   │
└──────────┬──────────┘
           │ architecture
           ▼
┌─────────────────────┐
│   CODER PLAN NODE    │  ← Plans which files to generate
│   Uses architecture  │     (e.g., backend/app.py, frontend/src/App.jsx)
└──────────┬──────────┘
           │ file_plan
           ▼
┌─────────────────────┐
│   CODER FILE NODE    │  ← Generates COMPLETE file contents for each file
│   (70B model, 16K)   │     Iterates through file_plan one file at a time
│   Output: Raw code   │
└──────────┬──────────┘
           │ files (dict: path → content)
           ▼
┌─────────────────────┐
│   WRITE FILES NODE   │  ← Writes files to disk
│   + Contract Builder │     Extracts Flask routes → builds contract.json
│                      │     Validates Python syntax, fixes common bugs
└──────────┬──────────┘
           │ extracted_routes, request_fields
           ▼
┌─────────────────────┐
│     TEST NODE        │  ← Starts Flask backend, runs contract tests
│   Contract Tester    │     Tests each endpoint (GET/POST/PUT/DELETE)
└──────────┬──────────┘
           │
           ├── pass ──────────────────────────────┐
           │                                       ▼
           ├── fail (retries < 3) ──┐      ┌─────────────┐
           │                        ▼      │  PREVIEW     │
           │                 ┌────────────┐│  NODE        │
           │                 │  REPAIR    ││  Starts:     │
           │                 │  NODE      ││  - Flask:5000│
           │                 │  (70B, fix)││  - Vite:5173 │
           │                 └─────┬──────┘│  + Patching  │
           │                       │       └──────┬──────┘
           │                       └──→ CODER_FILE│
           │                                      ▼
           └── fail (retries ≥ 3) ──→      ┌─────────┐
                                           │   END   │
                                           └─────────┘
```

### 2.2 SDLC Planning Pipeline

Each SDLC stage is a **standalone single-node LangGraph** that can be executed independently:

| Stage | Node | Schema | Key Outputs |
|-------|------|--------|-------------|
| 1. Overview | `overview_node` | `ProjectOverviewOutput` | title, goals, audience, KPIs, timeline |
| 2. Requirements | `requirements_node` | `RequirementsOutput` | FR list, NFR list, constraints, assumptions |
| 3. User Research | `user_research_node` | `UserResearchOutput` | roles, personas, empathy maps |
| 4. Task Flows | `task_flows_node` | `TaskFlowsOutput` | flows with steps, connections, decision nodes |
| 5. User Stories | `user_stories_node` | `UserStoriesOutput` | epics → sprints → stories with acceptance criteria |

**Stage-Gated Execution**: Each stage runs only when explicitly triggered via the UI. The user can review, approve, or re-run each stage before proceeding.

### 2.3 Chat Refinement Pipeline

A simpler 3-node graph for modifying existing projects:

```
User follow-up message
    │
    ▼
┌─────────────────────┐
│     CHAT NODE        │  ← Analyzes existing files + user request
│   (8K tokens)        │     Outputs: modified_files (complete replacements)
└──────────┬──────────┘
           │ files (merged)
           ▼
┌─────────────────────┐
│   WRITE FILES        │  ← Writes updated files to disk
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     PREVIEW          │  ← Restarts preview with updated code
└─────────────────────┘
```

---

## 3. Component Architecture

### 3.1 Backend Components

#### `app/core/llm.py` — Multi-Provider LLM Engine

```python
# Architecture:
#
# get_llm(role) → FallbackLLM
#                    │
#                    ├── primary: ChatGroq (Groq API)
#                    │     └── model: llama-3.3-70b (code gen) or llama-3.1-8b (SDLC)
#                    │
#                    ├── fallback: ChatGoogleGenerativeAI (Gemini API)
#                    │     └── model: gemini-2.5-flash
#                    │
#                    └── _generate():
#                          1. Try primary
#                          2. If rate-limited → try fallback
#                          3. If both fail → wait (extract delay from error) → retry
#                          4. Max 2 retries
```

**Token Limits by Role:**

| Role | Max Tokens | Rationale |
|------|-----------|-----------|
| strategist | 4,000 | Structured JSON output |
| architect | 4,000 | Structured JSON output |
| coder | 16,000 | Complete file generation |
| repair | 16,000 | Complete file rewrite |
| chat | 8,000 | Incremental modifications |
| sdlc | 4,000 | Planning documents |

#### `app/core/state.py` — Shared Pipeline State

The `ProjectState` TypedDict contains **25+ fields** organized in 6 categories:
1. **User Input**: prompt, chat history, is_followup flag
2. **Project Config**: name, directory, tech stack
3. **Agent Outputs**: project_scope, architecture, contract
4. **SDLC Stages**: overview, requirements, user_research, task_flows, user_stories
5. **Code Generation**: file_plan, files, routes, generation_issues
6. **Testing & Preview**: tests_passed, repair_attempts, preview_url

#### `app/core/database.py` — SQLite Persistence

5 tables with foreign key cascades:

```sql
projects            -- id, name, prompt, tech_stack, status, project_dir
├── generated_files -- project_id → file_path, content, size
├── chat_messages   -- project_id → role, content, msg_type
├── sdlc_stages     -- project_id → stage_name, stage_data (JSON)
└── project_versions -- project_id → version_num, files_json (snapshot)
```

#### `web_ui.py` — Flask Web Server

- **18 REST API routes** across 5 route groups
- **4 Socket.IO events** for real-time communication
- **SSE endpoint** for streaming pipeline progress
- **Background threading** for non-blocking generation
- **SPA fallback** to serve React app for client-side routing

### 3.2 Frontend Components

| Component | Purpose | Key Props |
|-----------|---------|-----------|
| `App.jsx` | Route definitions | — |
| `ProjectsPage` | Dashboard with project cards | — |
| `EditorView` | Main IDE layout (chat + code + preview) | — |
| `ChatPanel` | Message input/output with step indicators | width, messages, onSend |
| `CodePanel` | File tree + Monaco editor | files, activeFile, onOpenFile |
| `FileTree` | Hierarchical file explorer | files, onSelect |
| `EditorPane` | Monaco code editor wrapper | content, language |
| `PreviewPanel` | Iframe with preview controls | previewUrl, onStartPreview |
| `Header` | Top nav with project name, actions | projectName, isGenerating |
| `StatusBar` | Bottom bar with step/test status | currentStep, filesCount |
| `ResizeHandle` | Draggable panel divider | onResize |
| `StageSidebar` | SDLC stage navigation | stages, activeStage |
| `VersionHistory` | Snapshot list with restore | projectId |

**Custom Hook: `useGeneration.js`**
- Manages all generation state (files, messages, status, preview)
- SSE event stream subscription for real-time updates
- API calls for generate, chat, preview, and project loading
- Auto-opens first file when generation completes

---

## 4. Data Flow

### 4.1 New Project Generation Flow

```
1. User types prompt in ChatPanel
2. ChatPanel → sendPrompt() in useGeneration hook
3. Hook sends POST /api/generate with { prompt }
4. Hook opens SSE stream at /api/stream
5. web_ui.py starts _run_generation() in background thread
6. _run_generation() calls run_pipeline_streaming() from app/main.py
7. Pipeline runs: strategist → architect → coder_plan → coder_file → write_files → test
8. After each node, on_node_complete callback updates _current_state
9. SSE stream polls _current_state every 300ms, sends diffs to client
10. Client receives SSE events → updates files, steps, status in React state
11. Pipeline completes → auto-starts preview (Flask:5000 + Vite:5173)
12. Preview URL sent via SSE → PreviewPanel loads iframe
13. Project saved to SQLite with files, messages, generated code
```

### 4.2 SDLC Stage Execution Flow

```
1. User clicks "Run" on a specific stage in StageSidebar
2. POST /api/stages/run/<stage_name> with { prompt }
3. web_ui.py builds single-node LangGraph for that stage
4. LangGraph invokes the stage node (e.g., overview_node)
5. Node uses LLM with role-specific Pydantic output parser
6. Result stored in _current_state (e.g., "project_overview": {...})
7. Result persisted to sdlc_stages table in SQLite
8. Client polls/receives updated stage data → renders in stage page
```

### 4.3 Preview System Flow

```
1. preview_node receives ProjectState with files + project_dir
2. Stop any existing preview processes
3. Kill stale processes on ports 5000 and 5173
4. Patch backend/app.py: ensure CORS, correct port, host 0.0.0.0
5. Patch vite.config.js: fix proxy, add CSP headers
6. Patch all .jsx files: remove hardcoded localhost URLs
7. Auto-inject missing component imports
8. Create CSS stubs for missing stylesheets
9. Remove imports for non-existent files
10. Install backend deps (pip install -r requirements.txt)
11. Scan imports, patch package.json with missing npm packages
12. Install frontend deps (npm install)
13. Start Flask backend (subprocess.Popen)
14. Health check backend with retries
15. Start Vite dev server (npx vite)
16. Health check frontend with retries
17. Return preview_url (http://127.0.0.1:5173)
```

---

## 5. Technology Stack Summary

| Layer | Technology | Version |
|-------|-----------|---------|
| **AI Framework** | LangGraph + LangChain | Latest |
| **Primary LLM** | Groq (Llama 3.3 70B) | API |
| **Fallback LLM** | Google Gemini (Flash) | API |
| **Backend Framework** | Flask + Flask-SocketIO | Latest |
| **Frontend Framework** | React 19 + Vite 7 | Latest |
| **UI Libraries** | Monaco Editor, Lucide Icons, XYFlow | Latest |
| **State Management** | React hooks (useState, useEffect, useCallback) | — |
| **Database** | SQLite (via sqlite3) | Built-in |
| **Schema Validation** | Pydantic v2 | Latest |
| **Real-time** | SSE + Socket.IO | — |
| **Generated Backend** | Flask + flask-cors | Latest |
| **Generated Frontend** | React 18 + Vite + Axios | Latest |

---

## 6. Security Considerations

| Concern | Current Status |
|---------|---------------|
| API keys in `.env` | ✅ `.gitignore` excludes `.env` |
| LLM output sanitization | ✅ JSON sanitizer + code validator |
| SQL injection | ✅ Parameterized queries throughout |
| Generated code execution | ⚠️ Runs in subprocess (same machine) — consider Docker isolation |
| CORS | ✅ Flask-CORS enabled; generated apps use CORS too |
| File system access | ⚠️ Generated projects write to workspace dir |

---

## 7. Deployment Options

### Local Development (Current)
```bash
# Terminal 1
python web_ui.py           # Flask backend on :8080

# Terminal 2
cd client && npm run dev   # Vite dev server on :3000
```

### Production Build
```bash
cd client
npm run build              # Outputs to client/dist/
cd ..
python web_ui.py           # Serves React from client/dist/ + API
```
Access at **http://localhost:8080** (no separate Vite server needed).

### Docker (Planned)
- Containerize Flask + React build
- Isolate generated project execution in sandboxed containers
- Docker Compose for multi-service deployment

---

## 8. Versioning Strategy

| Version | Milestone | Status |
|---------|-----------|--------|
| v1.0 | Core pipeline (CLI) | ✅ Complete |
| v2.0 | Web IDE (React + Flask) | ✅ Complete |
| v3.0 | SDLC Planning (5 stages) | ✅ Complete |
| v3.1 | Data Persistence (SQLite) | ✅ Complete |
| v3.2 | Reliability (fallback LLM, auto-patching) | ✅ Complete |
| v4.0 | Multi-stack support + Docker isolation | 📝 Planned |
| v5.0 | Multi-user + GitHub integration | 📝 Planned |
