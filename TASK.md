# 📋 AI Code Factory — Task Tracker

> Living task document tracking current status, completed work, and upcoming features.

---

## ✅ Completed Tasks

### Phase 1: Core Pipeline (v1.0)
- [x] LangGraph-based code generation pipeline
- [x] Strategist Agent — requirement analysis from natural language
- [x] Architect Agent — system design (backend routes + frontend components)
- [x] Coder Agent — full Flask + React code generation with file planning
- [x] Write Files Node — disk persistence + API contract extraction
- [x] Contract Testing — automated API endpoint validation
- [x] Repair Agent — self-healing loop with up to 3 retry attempts
- [x] Preview Node — live Flask + Vite preview with health checks
- [x] CLI entry point (`run_factory.py`)

### Phase 2: Web IDE (v2.0)
- [x] Flask web server (`web_ui.py`) serving React SPA
- [x] React + Vite frontend (`client/`)
- [x] Chat Panel — natural language project generation/refinement
- [x] Code Panel — file tree + Monaco editor with syntax highlighting
- [x] Preview Panel — embedded live preview iframe
- [x] SSE Streaming — real-time step-by-step progress updates
- [x] WebSocket support (Socket.IO) for bidirectional communication
- [x] Responsive resizable panels with drag handles
- [x] Status bar with pipeline progress indicators

### Phase 3: SDLC Planning (v3.0)
- [x] 5-stage SDLC planning pipeline:
  - [x] Stage 1: Project Overview (title, goals, audience, KPIs)
  - [x] Stage 2: Requirements (FR/NFR with priorities)
  - [x] Stage 3: User Research (roles, personas, empathy maps)
  - [x] Stage 4: Task Flows (user journey diagrams)
  - [x] Stage 5: User Stories (epics, sprints, story points)
- [x] Pydantic schemas for all SDLC stage outputs
- [x] Stage-gated execution (each stage runs independently)
- [x] SDLC stage pages in React UI:
  - [x] OverviewPage
  - [x] RequirementsPage
  - [x] UserResearchPage
  - [x] TaskFlowsPage (with visual flow diagrams)
  - [x] UserStoriesPage
- [x] Stage sidebar navigation component

### Phase 4: Data Persistence (v3.1)
- [x] SQLite database (`projects.db`)
- [x] Project CRUD (save, load, list, delete)
- [x] Generated file storage in DB
- [x] Chat message persistence
- [x] SDLC stage data persistence per project
- [x] Version history with snapshot/restore
- [x] Projects dashboard page with search/filter

### Phase 5: Reliability & DX (v3.2)
- [x] Multi-provider LLM with auto-fallback (Groq ↔ Gemini)
- [x] Rate-limit detection and automatic retry with backoff
- [x] SDLC stages use cheaper/faster models to avoid API throttling
- [x] Preview node: auto-patch localhost URLs → relative paths
- [x] Preview node: auto-inject missing JSX component imports
- [x] Preview node: create CSS stubs for missing stylesheets
- [x] Preview node: fix broken imports referencing non-existent files
- [x] Preview node: patch `vite.config.js` for CORS/CSP headers
- [x] Project state reset when switching projects (prevent stale data)
- [x] Chat refinement pipeline (modify existing projects)
- [x] Download project as ZIP

---

## 🚧 In Progress

- [ ] Enhanced error handling and user-facing error messages
- [ ] Improved UI responsiveness on mobile/tablet screens

---

## 📝 Planned / Backlog

### Near-Term
- [ ] Project rename and duplicate functionality
- [ ] Per-project download (currently downloads active project only)
- [ ] Diff viewer for version comparisons
- [ ] Multiple tech stack support beyond `react-flask` (e.g., Next.js, Vue + Flask)
- [ ] Export SDLC documents as PDF
- [ ] Stage edit/regenerate with user feedback integration

### Medium-Term
- [ ] Docker containerization for generated projects
- [ ] One-click deployment (Vercel, Railway, etc.)
- [ ] Multi-file simultaneous code generation (parallel coder agents)
- [ ] AI code review agent
- [ ] Component library detection and auto-import (MUI, Chakra, etc.)
- [ ] Authentication scaffolding for generated projects

### Long-Term
- [ ] Multi-user support with project sharing
- [ ] GitHub integration (push generated code to repo)
- [ ] CI/CD pipeline generation
- [ ] Plugin system for custom agents
- [ ] Support for additional backend frameworks (Express, FastAPI, Django)
- [ ] AI-powered design system generation
- [ ] Real-time collaborative editing

---

## 🐞 Known Issues

| Issue | Status | Notes |
|-------|--------|-------|
| Groq rate limits during heavy generation | Mitigated | Auto-fallback to Gemini + retry with backoff |
| LLM occasionally generates truncated files | Mitigated | Repair agent + preview patching |
| Port conflicts on 5000/5173 | Handled | Preview node kills stale processes |
| `package.json` missing dependencies | Fixed | Auto-scan imports and patch before `npm install` |
| Stale SDLC data across projects | Fixed | Full state replacement on project load |

---

## 📊 Metrics

| Metric | Value |
|--------|-------|
| **Total Python files** | ~40+ |
| **Total React components** | 10 |
| **Total pages** | 7 (dashboard + editor + 5 SDLC stages) |
| **Graph nodes** | 21 |
| **API endpoints** | 18 |
| **Database tables** | 5 |
| **LLM agents** | 6 (strategist, architect, coder, tester, repair, chat) |
