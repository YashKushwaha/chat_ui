import pandas as pd
import re

from utils.patient_data_manager import PatientDataStore
import pyperclip

class DataAgent:
    def __init__(self, llm: str, dataframe: pd.DataFrame):
        self.llm = llm
        self.dataframe = dataframe

    def construct_prompt(self, question: str) -> str:
        """
        Constructs the prompt for the LLM using the provided question and a sample of the dataframe.
        """
        return f"""
        You are a data assistant. Here's a sample of the data:
        {self.dataframe.head(5).to_markdown()}
        The user asked: {question}
        Write Python code to answer the question using the DataFrame 'df'. Only return code.
        """
    def construct_prompt_with_metadata(self, question: str, metadata:str) -> str:
        """
        Constructs the prompt for the LLM using the provided question and includes metadata to explain column names.
        """   
        # Format the prompt with metadata and a sample of the data
        return f"""
            You are a data assistant. Here is the metadata explaining the columns:
            {metadata}
            Here's a sample of the data:
            {self.dataframe.head(5).to_markdown()}
            The user asked: {question}
            Write Python code to answer the question using the DataFrame 'df'. Only return code.
            """
    def construct_from_for_single_data_point(row_num = 0):
        pass

    def extract_code(self, response_text: str) -> str:
        """
        Extracts the Python code from the LLM's response text.
        You can use regex or other methods to sanitize the response.
        """
        match = re.search(r"```python\n(.*?)\n```", response_text, re.DOTALL)
        if match:
            return match.group(1)
        return response_text.strip()

    def execute_code(self, code: str):
        """
        Executes the provided Python code (for simplicity, using `exec()`).
        This should be sandboxed in production.
        """
        try:
            # Create a safe execution environment
            exec_locals = {"df": self.dataframe}
            exec(code, {}, exec_locals)
            return exec_locals
        except Exception as e:
            return f"Error executing code: {e}"

    def query(self, question: str):
        """
        Main method to query the agent with a question.
        """
        prompt = self.construct_prompt(question)
        response = self.llm(prompt, max_tokens=512)
        code = self.extract_code(response['choices'][0]['text'])
        result = self.execute_code(code)
        return result

def test_patient_store():
    store = PatientDataStore()
    patient_data = store.patient_data
    print('shape -> ', patient_data.shape)
    data_points = '\n'.join(patient_data.columns)
    single_record = store.get_patient_record(5)
    print('single_record -> \n', single_record)
    print('data_points -> \n', data_points)

if __name__ == '__main__':


    #prompt = store.get_prompt_for_single_patient(data_points, single_record)
    agent  = DataAgent(llm=None, dataframe=None)
    server_response = """Certainly! You can create a dummy DataFrame using the `pandas` library. Here's a simple example of how to do this:\n\n```python\nimport pandas as pd\n\n# Create a dummy DataFrame with some values\ndata = {\n    'Name': ['Alice', 'Bob', 'Charlie'],\n    'Age': [25, 30, 35],\n    'City': ['New York', 'Los Angeles', 'Chicago']\n}\n\n# Convert the dictionary to a DataFrame\ndf = pd.DataFrame(data)\n\n# Display the DataFrame\nprint(df)\n```\n\nThis code will create and print a DataFrame with three columns: `Name`, `Age`, and `City`, each containing some sample data. Make sure you have `pandas` installed in your Python environment, which you can do using `pip install pandas`."""

    code = agent.extract_code(server_response)
    print('Code to be executed')
    print(5*'=')
    print(code)
    print(5*'=')

    exec_locals = agent.execute_code(code)
    print(5*'=')
    for i,j in exec_locals.items():
        print(i)
        print(j)
        print(5*'-')
    #question = 'How many smokers in the dataset?'
    #prompt = agent.construct_prompt(question)
    #pyperclip.copy(prompt)
