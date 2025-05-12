from jinja2 import Template
import json
from .utils import get_patient_data_metadata

table_details = get_patient_data_metadata()

FIRST_PROMPT_TEMPLATE = """
SYSTEM:

You are medical expert  with access to patient datasets. 
You may have to write Python code to join tables and use a tool to execute it.
You also have access to variety of tools for different purposes.

Here is the list of tables that will be helpful to answer user query. List of columns in the table and description of table column is also provided.
{{table_details}}

If tool usage required, answer in the following format -

Thought: [reasoning]
Action: [tool_name]
Action Input: [JSON input]

Only use tools when needed. Available tools:
- fetch_health_data(patient_id) - returns all records available in the database for a given patient id from the health data table. Note it cant return the entire dataset

USER:
{{user_query}}
"""
FIRST_PROMPT_TEMPLATE = Template(FIRST_PROMPT_TEMPLATE)

class MedicalDataExpertAgent:
    def __init__(self, llm, table_details=None):
        self.llm = llm

    def run(self, user_query):
        prompt = FIRST_PROMPT_TEMPLATE.render(table_details=table_details, user_query=user_query)
        print(10*'=')
        print('MedicalDataExpertAgent being run')
        print(10*'=')
        print('prompt', prompt)
        response = self.llm.generate(prompt)

        # Check if it's an agent invocation
        if "Action:" in response:
            action_line = next(line for line in response.splitlines() if line.startswith("Action:"))
            input_line = next(line for line in response.splitlines() if line.startswith("Action Input:"))

            agent_name = action_line.split("Action:")[1].strip()
            #agent_input = eval(input_line.split("Action Input:")[1].strip())  # Safer to use json.loads() if JSON
            agent_input = input_line.split("Action Input:")[1].strip()
            print('agent_name -> ', agent_name)
            print('agent_input -> ', agent_input)

        return response