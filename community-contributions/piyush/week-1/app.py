import re
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from tools.amazon_tool import search_amazon_products

app = FastAPI()
memory = InMemorySaver()

SYSTEM_PROMPT = """
    You are amazon india assitant that help to find best product under user budget
    use search_amazon_products when you need live product data
    if the user ask follow up question about products already found in the chat
    answer from conversation memory instead of search again
    CRITICAL: if search_amazon_products returns an error or empty list then don't retry just tell / return appropriate message to user
    Format recommendations cleanly with product name, price (INR), rating, link, and a 1-line reason.
"""

INJECTION_PATTERNS = [
    r"ignore (all )?(previous|above) instructions",
    r"reveal (your )?system prompt",
    r"bypass (your )?rules",
    r"act as a ",
]

def run_input_guardrail(message: str) -> str | None:
    """Returns a refusal string if blocked, or None if safe."""
    text = message.lower().strip()

    if not text:
        return "Please enter a product or question."
    if len(text) > 500:
        return "Please keep your query under 500 characters."

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            print(f"[Guardrail] Blocked prompt injection: {message}")
            return "I can only help you search and compare products on Amazon India."

    return None

# ---------------------------------------------------------
# 2. LLM GATEWAY (Primary Model + Automatic Fallback)
# ---------------------------------------------------------
MODELS = [
    "groq:openai/gpt-oss-120b",        # Primary (smarter)
    "groq:openai/gpt-oss-20b",    # Fallback (fast backup)
]


agents={}
for model_name in MODELS:
    agents[model_name] = create_agent(
        model=model_name,
        tools=[search_amazon_products],
        checkpointer=memory,
        system_prompt=SYSTEM_PROMPT,
    )

def invoke_via_gateway(message: str, thread_id: str) -> dict:
    """Tries Primary model first; automatically fails over to Fallback on error."""
    last_error = None
    print(message)
    for model_name in MODELS:
        try:
            print(f"[Gateway] Routing request to: {model_name}")
            response = agents[model_name].invoke(
                {"messages": [{"role": "user", "content": message}]},
                config={
                    "recursion_limit": 6,
                    "configurable": {"thread_id": thread_id},
                },
            )
            return {
                "reply": response["messages"][-1].content,
                "model_used": model_name,
            }
        except Exception as e:
            print(f"[Gateway] {model_name} failed: {e}")
            last_error = e

    return {
        "reply": f"All models are currently unavailable. Last error: {last_error}",
        "model_used": "none",
    }

# ---------------------------------------------------------
# 3. FASTAPI ROUTES
# ---------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    thread_id: str = "shopping_session_1"

@app.get("/")
def serve_ui():
    return FileResponse("index.html")

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    # Step A: Guardrail runs BEFORE any LLM call
    refusal = run_input_guardrail(req.message)
    if refusal:
        return {"reply": refusal, "model_used": "guardrail_blocked"}

    # Step B: Route through LLM Gateway
    return invoke_via_gateway(req.message, req.thread_id)