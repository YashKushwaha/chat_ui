from .factory import load_llm

#from src.prompts import get_prompt_template  # assuming prompt handling is separate

def extract_tags_from_text(question: str, llm) -> str:
    #llm = load_llm(config["llm"])
    prompt = f"Extract 3-5 relevant topic tags from the following text, output should be a comma separated list. Do not include any numbering or explanation:\n\n{question}\n\nTags:"
    response = llm.generate(prompt)
    tags = [tag.strip() for tag in response.split(",")]
    return tags