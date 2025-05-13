from .patient_data_manager import PatientDataStore, get_patient_data_metadata
import re
import json
from typing import Optional, Tuple

def extract_agent_action_old(response: str) -> Optional[Tuple[str, dict]]:
    """
    Extracts the agent name and JSON input from an LLM response.
    Looks for plain text 'Action:' and 'Action Input:' lines.
    """
    try:
        # Find line with 'Action:'
        action_line = next(
            (line for line in response.splitlines() if "Action:" in line), None)
        # Find line with 'Action Input:'
        input_line = next(
            (line for line in response.splitlines() if "Action Input:" in line), None)

        if not action_line or not input_line:
            print("No action or input match found.")
            return None

        agent_name = action_line.split("Action:")[1].strip()
        json_str = input_line.split("Action Input:")[1].strip()

        # Ensure it's a valid JSON
        agent_input = json.loads(json_str)

        return agent_name, agent_input

    except Exception as e:
        print("Failed to extract action:", e)
        return None
    
def extract_agent_action(text):
    action_match = re.search(r"Action:\s*(\w+)", text)
    input_match = re.search(r"Action Input:\s*({.*})", text, re.DOTALL)

    if not action_match or not input_match:
        return None
        #raise ValueError("No actionable agent found.")

    action = action_match.group(1).strip()
    action_input_str = input_match.group(1).strip()

    try:
        action_input = json.loads(action_input_str)
    except json.JSONDecodeError as e:
        print('action_input_str -> ',action_input_str)
        raise ValueError(f"Failed to extract action: {e}")
        return ('', '')
    return action, action_input