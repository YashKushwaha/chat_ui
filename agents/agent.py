import json
from .utils import PatientDataStore, get_patient_data_metadata

# Initial user input

patient_data_store = PatientDataStore()
table_details = get_patient_data_metadata()

system_prompt_old = """You are an intelligent assistant with access to tools. Use this format:
Thought: [reasoning]
Action: [tool_name]
Action Input: [JSON input]

Only use tools when needed. Available tools:
- fetch_health_data(patient_id) - returns records available for a patient using the patient_id
- eval_code(code) - 

"""

system_prompt = """
You are medical expert  with access to patient datasets. 
You may have to write Python code to join tables and use a tool to execute it.
You also have access to variety of tools for different purposes.

Here is the list of tables that will be helpful to answer user query. List of columns in the table and description of table column is also provided.
{table_details}

If tool usage required, answer in the following format -

Thought: [reasoning]
Action: [tool_name]
Action Input: [JSON input]

Only use tools when needed. Available tools:
- fetch_health_data(patient_id) - returns all records available in the database for a given patient id from the health data table. Note it cant return the entire dataset
- eval_code(code) - can execute python code. useful for user queries that requires joining health data table and the activity data table

"""

medical_expert = """
SYSTEM:

You are a healthcare expert. You will be provided data points from patient report.
You have to analyze the data points and answer user query.

USER:
{}"""

def agent_call(question, llm, stream = False):
    user_prompt = question
    prompt = f"SYSTEM:\n{system_prompt}\nUSER:\n{user_prompt}"
    response = llm.generate(prompt, stream=stream)
    print('response -> ', response)
    # Step 2: Parse action and input
    lines = response.strip().splitlines()
# Check if Action is present
    action_line = next((line for line in lines if line.startswith("Action:")), None)
    input_line = next((line for line in lines if line.startswith("Action Input:")), None)

    print('action_line -> ', action_line)
    print('input_line -> ', input_line)
    
    
    
    if action_line and input_line:
        tool_name = action_line.replace("Action:", "").strip()
        if tool_name == 'fetch_health_data':
            tool_args = json.loads(input_line.replace("Action Input:", "").strip())
            tool_output = patient_data_store.get_patient_record(**tool_args)
            patient_data = patient_data_store.convert_data_point_to_text(tool_output)        
            new_prompt = medical_expert.format(patient_data)     
            new_prompt = f'{new_prompt}\n{user_prompt}'   
            print('new_prompt -> ', new_prompt)
            final_response = llm.generate(new_prompt)
    else:
        print("Direct LLM response:")
        final_response = response
    return final_response


# Step 1: Ask the LLM to decide on a tool
if __name__ == '__main__':
    response = llm.generate(prompt, stream=stream)
    response = call_llm(prompt)

    # Step 2: Parse action and input
    lines = response.strip().splitlines()
    action_line = next(line for line in lines if line.startswith("Action:"))
    input_line = next(line for line in lines if line.startswith("Action Input:"))

    tool_name = action_line.replace("Action:", "").strip()
    tool_args = json.loads(input_line.replace("Action Input:", "").strip())

    # Step 3: Call the tool
    tool = TOOLS[tool_name]
    tool_output = tool(**tool_args)

    # Step 4: Feed back the observation to the LLM
    new_prompt = f"{response}\nObservation: {json.dumps(tool_output)}"
    final_response = call_llm(new_prompt)

    print("\n=== Final Answer ===")
    print(final_response)
