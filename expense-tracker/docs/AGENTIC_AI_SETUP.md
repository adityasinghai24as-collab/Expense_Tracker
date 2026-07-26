# 🤖 Agentic AI Setup & Implementation Guide

This guide provides step-by-step instructions on how to implement the **Autonomous Financial Advisor** and other advanced Agentic AI features (RAG, Human-in-the-Loop, Self-Healing) in the Expense Tracker project.

**Goal**: Build a multi-agent system that runs entirely on the **Free Tier** using Google Gemini 1.5 Flash and local vector stores.

---

## 1. Prerequisites & Environment Setup

We will be using **LangChain** and **LangGraph** in Python.

### 1.1 Install Dependencies
Run the following in your `backend/` directory:
```bash
# Core LangChain & LangGraph
pip install langchain langgraph langchain-core

# Google Gemini Integration (Free Tier)
pip install langchain-google-genai

# Local RAG Dependencies (100% Free)
pip install chromadb sentence-transformers pypdf
```

### 1.2 Environment Variables
Add the following to your `backend/.env` file. You can get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/).

```env
GOOGLE_API_KEY=your_gemini_api_key_here
LANGCHAIN_TRACING_V2=true  # Optional: For LangSmith debugging
LANGCHAIN_API_KEY=your_langsmith_key_here
```

---

## 2. Core Architecture: The Multi-Agent State Machine

We use **LangGraph** to create a cyclic state machine. This is much more robust than a linear script.

### 2.1 Define the State
Create `backend/app/ai/state.py`:
```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_id: int  # Security: Lock state to the current user
    next_agent: str
    requires_approval: bool # For Human-in-the-loop
```

### 2.2 Create Fast API Tools
Turn your database queries into tools. Create `backend/app/ai/tools.py`:
```python
from langchain.tools import tool
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models import Expense

@tool
async def get_user_spending(user_id: int, month: int) -> str:
    """Gets total spending for the user in a given month."""
    async with AsyncSessionLocal() as db:
        # Secure query logic here
        return f"User spent $500."
```

### 2.3 Compile the Graph
Create `backend/app/ai/graph.py` to wire the agents together:
```python
from langgraph.graph import StateGraph, END
from .state import AgentState

workflow = StateGraph(AgentState)

# Define Nodes (Agents)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("action_executor", action_node)

# Define routing logic
workflow.set_entry_point("supervisor")
workflow.add_conditional_edges("supervisor", route_logic)

app_graph = workflow.compile()
```

---

## 3. Implementing Advanced Features

### Feature A: Human-in-the-Loop (HITL) for High-Stakes Actions
If the `action_executor` wants to delete data or change a budget, we pause the graph.
**How to implement:**
1. In `app_graph = workflow.compile()`, add an interrupt:
   ```python
   app_graph = workflow.compile(interrupt_before=["action_executor"])
   ```
2. When the graph runs and hits the `action_executor`, it yields a paused state.
3. The FastAPI endpoint returns a `402 Payment Required` or custom `202 Accepted` status with a payload `{"status": "waiting_for_approval", "action": "delete_expenses"}`.
4. The frontend UI shows an [Approve] / [Reject] button.
5. If approved, the frontend hits a resume endpoint: `app_graph.resume(state_id)`.

### Feature B: Local RAG (Financial Document Chat)
Allow users to query their bank statements.
**How to implement:**
1. **Ingestion**: When a user uploads a PDF, use `PyPDFLoader` to parse the text.
2. **Chunking**: Split the text using `RecursiveCharacterTextSplitter`.
3. **Embeddings**: Use HuggingFace embeddings (runs locally, free) to turn text into vectors.
   ```python
   from langchain_community.embeddings import HuggingFaceEmbeddings
   embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
   ```
4. **Vector Store**: Save the vectors into a local ChromaDB instance.
5. **Retrieval**: Give the `Analyst` agent a new tool: `@tool def query_bank_statements(query: str):` which performs a similarity search on ChromaDB and returns the matching paragraphs.

### Feature C: Self-Healing Agents (Error Recovery)
If an agent fails (e.g., hallucinated a category), it should fix itself.
**How to implement:**
1. Wrap tool execution in a `try/except` block.
2. If an exception occurs, do NOT crash the API. Instead, return the error message as a `ToolMessage` back to the Agent.
3. Define a LangGraph edge that loops the Agent back on itself if the last message was a Tool Error.
4. The LLM will read the error ("Column 'foo' does not exist") and generate a corrected tool call autonomously.

---

## 4. Testing the Implementation

To run the AI pipeline locally:
1. Ensure your `.env` has the Google API key.
2. Start the backend: `docker compose up backend` or `python main.py`.
3. Use Postman or Swagger to send a POST request to `/ai/chat`:
   ```json
   {
       "prompt": "How much did I spend on food this month?"
   }
   ```
4. Verify the backend console logs to watch the LangGraph state machine transition from Supervisor -> Analyst -> Final Answer.
