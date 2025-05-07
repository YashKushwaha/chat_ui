from .tools import TOOLS
from .rag_tools import rag_tool

# Define Support Agent
SUPPORT_AGENT_CONFIG = {
    "system_prompt": "You are a helpful support agent...",
    "tools": {
        "get_time": TOOLS["get_time"],
        "search_docs": rag_tool
    }
}

# Define RAG Agent
RAG_AGENT_CONFIG = {
    "system_prompt": "You are a RAG-based assistant. Always lookup relevant documents before answering.",
    "tools": {
        "search_docs": rag_tool
    }
}

# Define Finance Agent
FINANCE_AGENT_CONFIG = {
    "system_prompt": "You are a financial advisor. Assist users with banking, stock, and investment queries.",
    "tools": {
        "get_time": TOOLS["get_time"],
        "financial_data_tool": TOOLS.get("get_stock_price")  # for example
    }
}
