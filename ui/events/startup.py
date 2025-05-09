
from fastapi import FastAPI
from src.embedder import load_text_embedder
from src.vectorstore import load_vector_store
from src.llms import OllamaModel

# Pass config and model_list as parameters if needed
def create_startup_handler(app: FastAPI, config: dict, model_list: list):
    async def on_startup():
        app.state.embedder = load_text_embedder(config['embedding'])
        app.state.vectorstore = load_vector_store(config['vector_store'])

        llm_config = config['llm'][config['llm']['provider']]
        llm_config['model'] = ''.join([i for i in model_list if 'phi' in i])
        app.state.llm = OllamaModel(llm_config)

        app.state.settings = {
            "chat_history": False,
            "feature_x_enabled": True,
            "debug_mode": False,
        }

    return on_startup
