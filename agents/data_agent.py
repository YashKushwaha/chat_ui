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


if __name__ == '__main__':
    store = PatientDataStore()

    patient_data = store.patient_data

    print('shape -> ', patient_data.shape)

    #print(patient_data.head())
    #data_points = list(store.nominal_columns_with_mappings.keys())
    data_points = '\n'.join(patient_data.columns)
    single_record = store.get_patient_record(5)

    print('single_record -> \n', single_record)
    print('data_points -> \n', data_points)

    #prompt = store.get_prompt_for_single_patient(data_points, single_record)
    #agent  = DataAgent(llm=None, dataframe=patient_data)
    #question = 'How many smokers in the dataset?'
    #prompt = agent.construct_prompt(question)
    #pyperclip.copy(prompt)
