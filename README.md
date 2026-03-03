# ⚡ Multi-Agent Task Router

A **LangGraph-powered Multi-Agent Orchestration Framework** that intelligently routes user tasks to specialized AI agents using a **Router-Worker pattern** with a built-in **self-correction loop**.

---

## 🧠 Architecture

```
User Input
    │
    ▼
┌─────────┐       ┌──────────────┐
│  Router │──────▶│  Code Agent  │
│ (Fast   │       ├──────────────┤
│  8B LLM)│──────▶│Research Agent│
│         │       ├──────────────┤
└─────────┘──────▶│  Summarizer  │
                  ├──────────────┤
                  │General Agent │
                  └──────┬───────┘
                         │
                  ┌──────▼───────┐
                  │   Error?     │
                  │  Correction  │◀─── Self-Correction Loop (max 3 retries)
                  │   Agent      │
                  └──────────────┘
```

## ✨ Key Features

- **Conditional Routing** — Only the relevant agent is activated per request (~30% token savings)
- **Self-Correction Loop** — Agents automatically debug and refine failed outputs (up to 3 retries)
- **State Management** — Shared `AgentState` pipeline tracks task, result, errors, and trace logs
- **Dual Interface** — CLI (`main.py`) and Streamlit Web UI (`app.py`)
- **Single API Key** — Runs entirely on Groq (no other provider needed)

---

## 🤖 Agents & Models

| Agent | Model | Role |
|---|---|---|
| **Router** | `llama-3.1-8b-instant` | Classifies task type (fast, low-cost) |
| **Code Agent** | `llama-3.3-70b-versatile` | Writes, debugs, explains code |
| **Research Agent** | `llama-3.3-70b-versatile` | Answers questions, comparisons, facts |
| **Summarizer Agent** | `llama-3.3-70b-versatile` | Condenses and extracts key points |
| **General Agent** | `llama-3.3-70b-versatile` | Handles conversation and general queries |
| **Correction Agent** | `llama-3.3-70b-versatile` | Reviews failures and generates retry notes |

---

## 📁 Project Structure

```
Task_router/
├── .env                          # API key configuration
├── requirements.txt              # Python dependencies
├── main.py                       # CLI entry point
├── app.py                        # Streamlit web UI
├── state/
│   └── schema.py                 # Shared AgentState TypedDict
├── agents/
│   ├── router.py                 # Task classifier
│   ├── code_agent.py             # Coding specialist
│   ├── research_agent.py         # Research specialist
│   ├── summarizer_agent.py       # Summarization specialist
│   ├── general_agent.py          # General purpose agent
│   └── correction_agent.py       # Self-correction loop
└── graph/
    └── workflow.py               # LangGraph pipeline assembly
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/Task_router.git
cd Task_router
```

### 2. Create & activate virtual environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API key
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```
> Get a free API key at [console.groq.com](https://console.groq.com)

### 5. Run the app

**Streamlit UI (recommended):**
```bash
streamlit run app.py
```

**CLI mode:**
```bash
python main.py
```

---

## 💡 Example Tasks

| Input | Routed To |
|---|---|
| `"Write a Python function to reverse a string"` | Code Agent |
| `"What is the difference between TCP and UDP?"` | Research Agent |
| `"Summarize the following article: ..."` | Summarizer Agent |
| `"Hello, how are you?"` | General Agent |

---

## 🛠️ Tech Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — Agent graph orchestration
- **[LangChain](https://github.com/langchain-ai/langchain)** — LLM abstraction layer
- **[Groq](https://groq.com)** — Ultra-fast LLM inference
- **[Streamlit](https://streamlit.io)** — Web UI
- **[Pydantic](https://docs.pydantic.dev)** — State schema validation
- **Python 3.10+**

