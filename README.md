# 🏭 AI Code Factory

An AI-powered full-stack application generator that transforms natural language descriptions into working web applications.

## 🎯 What It Does

Given a simple prompt like:
> "build a todo app where I can add, complete, and delete tasks"

The system automatically:
1. **Analyzes** the requirements (Strategist Agent)
2. **Designs** the architecture (Architect Agent)
3. **Generates** backend (Flask) and frontend (React) code (Coder Agent)
4. **Tests** the generated code (Contract Tests)
5. **Self-heals** if tests fail (Repair Agent - up to 3 attempts)
6. **Previews** the working application in your browser

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Hugging Face API key

### Setup

1. **Clone and install dependencies:**
```bash
cd A_Team_cursor
pip install -r requirements.txt
```

2. **Create `.env` file with your Hugging Face API key:**
```bash
HF_API_KEY=your_huggingface_api_key_here
```

3. **Run the factory:**
```bash
# Interactive mode
python run_factory.py

# Or with a prompt
python run_factory.py "build a note-taking app"
```

## 📁 Project Structure

```
A_Team_cursor/
├── app/
│   ├── main.py              # Entry point
│   ├── agents/              # AI agents (Strategist, Architect, Coder, Tester)
│   │   ├── strategist/      # Requirement analysis
│   │   ├── architect/       # System design
│   │   ├── coder/           # Code generation
│   │   └── tester/          # Test result processing
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   ├── llm.py           # LLM initialization (Qwen 72B/7B)
│   │   └── state.py         # Shared state definition
│   ├── graph/
│   │   ├── graph.py         # LangGraph workflow definition
│   │   ├── edges.py         # Conditional routing logic
│   │   └── nodes/           # All pipeline nodes
│   ├── runtime/
│   │   ├── contract_tester.py  # API contract testing
│   │   ├── test_runner.py      # Backend server management
│   │   └── preview.py          # Live preview system
│   └── workspace/
│       └── generated_projects/  # Output directory
├── run_factory.py           # Quick-run script
├── requirements.txt
└── README.md
```

## 🔄 Pipeline Flow

```
User Prompt
    │
    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ STRATEGIST  │ ──→ │  ARCHITECT  │ ──→ │ CODER_PLAN  │
│ (72B model) │     │ (72B model) │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
    │                                          │
    │ project_scope                            │ file_plan
    ▼                                          ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ CODER_FILE  │ ──→ │ WRITE_FILES │ ──→ │    TEST     │
│ (72B model) │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                          ┌────────────────────┼────────────────────┐
                          │                    │                    │
                          ▼                    ▼                    ▼
                    [TESTS PASS]         [TESTS FAIL]        [MAX RETRIES]
                          │                    │                    │
                          ▼                    ▼                    ▼
                    ┌─────────┐          ┌─────────┐          ┌─────────┐
                    │ PREVIEW │          │ REPAIR  │          │   END   │
                    └─────────┘          └─────────┘          └─────────┘
                          │                    │
                          │                    └──→ CODER_FILE (retry)
                          ▼
                    ┌─────────┐
                    │   END   │
                    └─────────┘
```

## 🤖 AI Models Used

| Agent | Model | Purpose |
|-------|-------|---------|
| Strategist | Qwen/Qwen2.5-72B-Instruct | Requirement analysis |
| Architect | Qwen/Qwen2.5-72B-Instruct | System design |
| Coder | Qwen/Qwen2.5-72B-Instruct | Code generation |
| Repair | Qwen/Qwen2.5-72B-Instruct | Bug fixing |

## 📝 Example Prompts

- "build a todo app with add, complete, and delete features"
- "create a calculator that can add, subtract, multiply, and divide"
- "make a note-taking app where I can create, edit, and delete notes"
- "build a simple expense tracker"
- "create a recipe book app"
- "make a contact list manager"

## 🛠️ Generated Stack

- **Backend**: Flask (Python) with in-memory storage
- **Frontend**: React 18 + Vite
- **API**: RESTful JSON endpoints
- **Testing**: Automated contract tests

## 📜 License

MIT License
