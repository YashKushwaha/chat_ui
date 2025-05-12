from jinja2 import Template
import re
import sys
import pandas as pd

from .utils.patient_data_manager import MetaDataManager, get_patient_data_metadata
import pyperclip

FIRST_PROMPT = """
SYSTEM:
You are a data expert. You will be given table names and their column names and description.
Assume that tables are already loaded into the Python environment with the same name as the table.
Your job is to convert user queries into pandas operations **only if** the query is analytical and requires data processing.

If the user input is not a data-related question (e.g., a greeting or unrelated topic), respond politely that you're here to help with data analysis and ask how you can assist.

If code is required, always wrap it in a `def run():` function and use `return` to output results instead of printing.

Table details:
{{table_details}}

USER:
{{user_query}}
"""
FIRST_PROMPT = Template(FIRST_PROMPT)

SECOND_PROMPT = """
SYSTEM:
You are a helpful data assistant. The user originally asked:
{{user_query}}
The following code was generated and executed to answer their question
```python
{{code_to_run}}
```

The output was 
```
{{output}}```

Given the results above, provide a clear and concise answer to the user's question. If any further interpretation or additional data is needed, include it in your response.
"""
SECOND_PROMPT = Template(SECOND_PROMPT)

def extract_code(response_text: str) -> tuple[bool, str]:
    """
    Extracts Python code from LLM response.
    Returns a tuple: (code_found, extracted_code_or_raw_response)
    """
    match = re.search(r"```python\n(.*?)\n```", response_text, re.DOTALL)
    if match:
        return True, match.group(1).strip()
    return False, response_text.strip()

def execute_code(code: str, exec_locals:dict):
    """
    Executes the provided Python code safely.
    The code must define a function `run()` which returns the result.
    """
    try:
        # Execution context with any necessary variables
        exec(code, exec_locals, exec_locals)

        # Call the function if defined
        if "run" in exec_locals:
            result = exec_locals["run"]()
            return result
        else:
            return "Error: No `run()` function found in code."

    except Exception as e:
        return f"Error executing code: {e}" 

TABLE_METADATA = get_patient_data_metadata()

class TabularDataExpertAgent:
    def __init__(self, llm, table_details=None):
        self.llm = llm
        self.table_details = table_details or TABLE_METADATA

    def run(self, user_query):
        prompt = FIRST_PROMPT.render(table_details=self.table_details, user_query=user_query) 
        print('prompt -> ', prompt)
        response = self.llm.generate(prompt)
        print('response -> ', response )
        has_code, code_to_run = extract_code(response)
        print('has_code -> ', has_code )
        print('code_to_run -> ', code_to_run )
        
        if has_code:
            health = pd.read_excel('/mnt/f/chat_ui/data/health_dataset.xlsx')
            activity = pd.read_excel('/mnt/f/chat_ui/data/activity_dataset.xlsx')
            exec_locals = dict(health=health, activity=activity, pd=pd)
            output = execute_code(code_to_run, exec_locals)

            second_prompt = SECOND_PROMPT.render(user_query=user_query, code_to_run=code_to_run, output=output)
            response = self.llm.generate(second_prompt)

        return response