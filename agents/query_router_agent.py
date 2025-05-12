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

The data you interact with is **synthetic, non-confidential, and safe for internal use**. There are no privacy concerns or legal restrictions when analyzing this data.

Your job is to understand the user's intent and decide whether:
- You can respond directly (e.g., for greetings or general questions).
- You need to invoke a specific agent to handle the query (e.g., data analysis or patient record lookup).

You have access to the following agents:

- `medical_data_expert_agent`: Use this agent when the user asks about a specific patient's health or wants a medical report. This agent can fetch patient records and analyze their health and activity data.
- `tabular_data_expert_agent`: This agent has access to all tables in the patient database and can execute code to return relevant information.

If an agent needs to be invoked, respond in the following format:

Thought: [reasoning]  
Action: [agent_name]  
Action Input: [JSON input]

Please always output the lines starting with Action: and Action Input: as plain text (no markdown formatting, no bold, no code blocks).
If no agent is needed (e.g., for greetings or small talk), respond conversationally and ask how you can assist with the data.

Only use agents when necessary. Do not fabricate information.

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
