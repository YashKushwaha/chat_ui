from jinja2 import Template
import json
from .utils import get_patient_data_metadata
from .utils import extract_agent_action, PatientDataStore

table_details = get_patient_data_metadata()

FIRST_PROMPT_TEMPLATE = """
SYSTEM:

You are medical expert  with access to patient datasets. 
You also have access to variety of tools for different purposes.

Here is the list of tables that will be helpful to answer user query. List of columns in the table and description of table column is also provided.
{{table_details}}

If tool usage required, answer in the following format -

Thought: [reasoning]
Action: [tool_name]
Action Input: [JSON input]

Please always output the lines starting with Action: and Action Input: as plain text (no markdown formatting, no bold, no code blocks).

Only use tools when needed. Available tools:
- fetch_health_data(patient_id) - returns all records available in the database for a given patient id from the health data table. Note it cant return the entire dataset

USER:
{{user_query}}
"""

SECOND_PROMPT_TEMPLATE = """
SYSTEM:

You are a healthcare expert. You will be provided data points from patient report.
You have to analyze the data points and answer user query.

USER:
{{user_query}}"""

FIRST_PROMPT_TEMPLATE = Template(FIRST_PROMPT_TEMPLATE)
SECOND_PROMPT_TEMPLATE = Template(SECOND_PROMPT_TEMPLATE)

patient_data_store = PatientDataStore()

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

        result = extract_agent_action(response)

        if result:
            agent_name, agent_input = result
            print("Agent Name:", agent_name)
            print("Agent Input:", agent_input)
            if agent_name == 'fetch_health_data':
                tool_args = agent_input
                tool_output = patient_data_store.get_patient_record(**tool_args)
                patient_data = patient_data_store.convert_data_point_to_text(tool_output)        
                new_prompt = SECOND_PROMPT_TEMPLATE.render(user_query = patient_data)     
                print('new_prompt -> ', new_prompt)
                response = self.llm.generate(new_prompt)
        else:
            print("No actionable agent found by medical expert.")

        return response
    
if __name__ == '__main__':
    response = """To gather information on the health of patient number 14, I will use the `fetch_health_data` tool to retrieve their records from the health data table. Once we have the data, we can analyze it based on available columns such as Age, BMI, Blood Pressure Abnormality, Chronic kidney disease, and other relevant factors.\n\n**Thought:** To understand the patient's health profile, I need to fetch the specific data for patient number 14 from the `health` table using the available tool.\n\n**Action:** fetch_health_data  \n**Action Input**: `{ \"patient_id\": 14 }`\n\nOnce I obtain the data, I will proceed with analyzing it."""
    print('User action -> ')
    print(5*'-')
    print(extract_agent_action(response))
    print(5*'-')