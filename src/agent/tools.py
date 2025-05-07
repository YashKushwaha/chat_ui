from src.rag_pipeline import generate_answer

def get_time(location: str) -> str:
    from datetime import datetime
    return f"The current time in {location} is {datetime.now().strftime('%H:%M:%S')}."

def call_rag(question: str) -> str:
    return generate_answer(question)

TOOLS = {
    "get_time": get_time,
    "call_rag": call_rag
}
