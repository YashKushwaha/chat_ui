# agent.py
import json
from tools import calculate, get_weather
from openai import OpenAI  # or Ollama equivalent

def call_tool(action: str, action_input: str) -> str:
    args = json.loads(action_input)
    if action == "calculate":
        return calculate(args["expression"])
    elif action == "get_weather":
        return get_weather(args["city"])
    return "Unknown tool"

def run_agent(user_input: str):
    system_prompt = open("prompt_template.txt").read()
    full_prompt = f"{system_prompt}\nUser: {user_input}\n"

    # Send to your LLM
    response = chat_with_llm(full_prompt)  # You write this using your LLM client
    print("LLM response:\n", response)

    # Parse LLM output
    lines = response.strip().split("\n")
    action_line = next((l for l in lines if l.startswith("Action:")), None)
    input_line = next((l for l in lines if l.startswith("Action Input:")), None)

    if action_line and input_line:
        tool_name = action_line.replace("Action:", "").strip()
        tool_input = input_line.replace("Action Input:", "").strip()
        result = call_tool(tool_name, tool_input)

        # Re-prompt LLM with Observation to get final answer
        new_prompt = f"{response}\nObservation: {result}\n"
        new_prompt += "Final Answer:"
        final_response = chat_with_llm(new_prompt)
        return final_response.strip()
    else:
        return response.strip()

# Replace this with actual LLM client
def chat_with_llm(prompt: str) -> str:
    # This can be an OpenAI call or Ollama call
    import openai
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        temperature=0
    )
    return completion['choices'][0]['message']['content']

if __name__ == "__main__":
    user_question = input("Ask me something: ")
    answer = run_agent(user_question)
    print("Agent:", answer)
