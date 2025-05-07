import re
class Agent:
    def __init__(self, llm, system_prompt: str, tools: dict):
        self.llm = llm
        self.system_prompt = system_prompt
        self.tools = tools

    def run(self, user_input: str) -> str:
        conversation_history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]

        while True:
            # Send the current conversation to the LLM
            prompt = self._format_prompt(conversation_history)
            llm_response = self.llm.generate(prompt).strip()
            print('LLM response -> ', llm_response)
            # Tool usage expected in format: use_tool:tool_name:tool_input
            match = re.search(r'CALL:\s*(\w+)\((.*?)\)', llm_response)
            if match:

                tool_name = match.group(1)
                raw_args = match.group(2)

                try:
                    tool_func = self.tools.get(tool_name)
                    if not tool_func:
                        tool_result = f"Error: Tool '{tool_name}' not found."
                    else:
                        tool_result = tool_func(raw_args)
                except Exception as e:
                    return f"Couldnt call the tool. Error -> {e}"

                return f'LLM asked to call tool:Tool Name : <{tool_name}>  Raw args : <{raw_args}>. Response -> {tool_result}'
            if llm_response.startswith("use_tool:"):
                try:
                    
                    _, tool_name, tool_input = llm_response.split(":", 2)
                except ValueError:
                    conversation_history.append({"role": "assistant", "content": "Invalid tool format."})
                    break

                tool_func = self.tools.get(tool_name)
                if not tool_func:
                    tool_result = f"Error: Tool '{tool_name}' not found."
                else:
                    tool_result = tool_func(tool_input)

                # Feed the tool result back to the LLM
                conversation_history.append({"role": "assistant", "content": llm_response})
                conversation_history.append({"role": "user", "content": f"Tool output: {tool_result}"})

            else:
                # Assume final response
                conversation_history.append({"role": "assistant", "content": llm_response})
                return llm_response

    def _format_prompt(self, history):
        """Turn chat history into a single string prompt."""
        return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])