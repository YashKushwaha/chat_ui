from jinja2 import Template
from utils.patient_data_manager import MetaDataManager
import pyperclip

class PromptManager:
    def __init__(self, prompt_dir="prompts"):
        self.prompt_dir = prompt_dir

    def load(self, name):
        with open(f"{self.prompt_dir}/{name}.txt") as f:
            return Template(f.read())
        
if __name__ == '__main__':
    file1 = '/mnt/f/chat_ui/data/health_metadata.xlsx'
    file2 = '/mnt/f/chat_ui/data/activity_metadata.xlsx'

    health_metadata = MetaDataManager(file1)
    activity_metadata = MetaDataManager(file2)

    health = health_metadata.get_column_descriptions(as_text=True)
    activity = activity_metadata.get_column_descriptions(as_text=True)
    content = f"""DataFrame ->  health\n{health}\n\nDataFrame -> activity\n{activity}\n"""

    name = 'table_details'
    #content  = 'Lorem ipsum'
    query = 'How do I get the list of male patients who smoke but also walk a lot every day ?'
    pm = PromptManager()
    prompt = pm.load(name)
    filled = prompt.render(content=content, query=query)
    pyperclip.copy(filled)
    print(filled)