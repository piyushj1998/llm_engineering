# Amazon AI Shopping Assistant & Product Scraper

An AI-powered shopping assistant and real-time Amazon product scraper built with **FastAPI**, **LangChain/LangGraph**, and **Groq**. It scrapes live product data with browser impersonation, enforces strict Pydantic structured outputs to prevent hallucinations, supports multi-session persistent chat memory, and streams responses via Server-Sent Events (SSE).

## Key Features

- **Real-Time Amazon Scraping:** Uses `curl_cffi` (browser impersonation) and `BeautifulSoup4` to reliably fetch and parse product details, pricing, and ratings.
- **Structured & Grounded Outputs:** Enforces strict `Pydantic` schemas (`ShoppingResponse`) with grounding rules to prevent LLM hallucinations and recursion loops.
- **Input Guardrails & Model Failover:** Validates incoming user queries before hitting the LLM and automatically falls back across Groq-hosted models if a primary model hits rate limits or errors.
- **Persistent Multi-Chat Memory:** Uses `langgraph-checkpoint-sqlite` (`SqliteSaver`) to persist conversation history across sessions in a local `chat_history.db`.
- **Real-Time Streaming:** Exposes a `/chat/stream` endpoint powered by Server-Sent Events (SSE) for responsive, token-by-token UI updates.

## Tech Stack

- **Backend & Streaming:** FastAPI, Uvicorn, Server-Sent Events (SSE)
- **AI & Orchestration:** LangChain, LangGraph, LangChain-Groq
- **Scraping & Parsing:** `curl_cffi`, BeautifulSoup4
- **Validation & Persistence:** Pydantic V2, SQLite (`langgraph-checkpoint-sqlite`)
- **Package Management:** `uv`

---

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) package manager
- A [Groq API Key](https://console.groq.com/)

## Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/<your-repo-name>.git
   cd <your-repo-name>