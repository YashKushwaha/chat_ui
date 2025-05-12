import json
import re
from typing import Optional, Tuple

from jinja2 import Template
from .medical_data_expert_agent import MedicalDataExpertAgent
from .table_expert_agent import TabularDataExpertAgent

from .utils import extract_agent_action

FIRST_PROMPT_TEMPLATE = """
SYSTEM:

You are a helpful medical assistant with access to patient datasets and a network of specialized agents.

The data you interact with is synthetic, non-confidential, and safe for internal use. There are no privacy concerns or legal restrictions when analyzing this data.

Your job is to understand the user's intent and decide whether:
- You can respond directly (e.g., for greetings or general questions).
- You need to invoke a specific agent to handle the query (e.g., data analysis or patient record lookup).

You have access to the following agents:

- medical_data_expert_agent: Use this agent when the user asks about a specific patient's health or wants a medical report. This agent can fetch patient records and analyze their health and activity data.
- tabular_data_expert_agent: This agent has access to all tables in the patient database and can execute code to return relevant information.

If an agent needs to be invoked, you must respond using this **exact format**, with no variation or formatting:

Thought: [Your reasoning]  
Action: [agent_name]  
Action Input: [JSON input]

⚠️ **Important formatting rules (strictly enforced)**:
- ✅ Use plain text only.  
- ✅ JSON must appear immediately below `Action Input:` with no extra line breaks.  
- ❌ Do NOT use backticks (`), triple backticks (```), bold (**), or indentation.  
- ❌ Do NOT put JSON in a markdown block or code block.  
- ❌ Do NOT quote the field names or wrap the response in extra markup.

✅ Example of correct format:

Thought: The user wants BMI grouped by physical activity, which requires a tabular SQL query.  
Action: tabular_data_expert_agent  
Action Input: {
  "query": "SELECT AVG(BMI), PhysicalActivityLevel FROM patient_records GROUP BY PhysicalActivityLevel"
}

If no agent is needed (e.g., for greetings or simple factual answers), respond conversationally.

Only invoke an agent when absolutely necessary. Never fabricate data or make assumptions not grounded in the input.

USER:
{{user_query}}
"""


FIRST_PROMPT_TEMPLATE = Template(FIRST_PROMPT_TEMPLATE)

AGENTS = {
    "medical_data_expert_agent": MedicalDataExpertAgent,
    "tabular_data_expert_agent": TabularDataExpertAgent
}

class QueryRouterAgent:
    def __init__(self, llm, table_details=None):
        self.llm = llm

    def run(self, user_query):
        prompt = FIRST_PROMPT_TEMPLATE.render(user_query=user_query)
        print(prompt)
        response = self.llm.generate(prompt)
        
        result = extract_agent_action(response)
        if result:
            agent_name, agent_input = result
            print("Agent Name:", agent_name)
            print("Agent Input:", agent_input)

            agent_to_run = AGENTS.get(agent_name)
            if agent_to_run and (agent_name == 'tabular_data_expert_agent'):
                agent = agent_to_run(llm=self.llm)
                response = agent.run(user_query)
            if agent_to_run and (agent_name == 'medical_data_expert_agent'):
                agent = agent_to_run(llm=self.llm)
                response = agent.run(user_query)
        else:
            print("No actionable agent found.")

        return response
