from jinja2 import Template
from utils.patient_data_manager import MetaDataManager, get_patient_data_metadata
import pyperclip

class PromptManager:
    def __init__(self, prompt_dir="prompts"):
        self.prompt_dir = prompt_dir

    def load(self, name):
        if not name.endswith('.txt'):
            name = f'{name}.txt'
        with open(f"{self.prompt_dir}/{name}") as f:
            return Template(f.read())
        
if __name__ == '__main__':
    query = 'How do I get the list of male patients who smoke but also walk a lot every day ?'
    pm = PromptManager()
    name = 'table_details'
    prompt = pm.load(name)
    content = get_patient_data_metadata()
    filled = prompt.render(content=content, query=query)
    pyperclip.copy(filled)
    print(filled)