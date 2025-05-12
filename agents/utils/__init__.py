from .patient_data_manager import PatientDataStore, get_patient_data_metadata
import re
import json
from typing import Optional, Tuple

def extract_agent_action(response: str) -> Optional[Tuple[str, dict]]:
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