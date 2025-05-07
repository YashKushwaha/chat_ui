from .base import BaseLLM
import requests
from openai import OpenAI
import os
import json

def token_stream(response):
    for line in response.iter_lines():
        if line:
            data = line.decode('utf-8')
            if data.startswith("data: "):
                data = data[6:]
            try:
                json_data = json.loads(data)
                yield json_data.get("response", "")
            except Exception as e:
                print("Stream decode error:", e)

class LlavaModel(BaseLLM):
    def __init__(self, config):
        self.model = config['model']
        self.url = config['url']

    def generate(self, prompt: str, image) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream" : False, "images": [image]}           
        response = requests.post(self.url, json=payload)
        return response.json()['response']

class OllamaModel(BaseLLM):
    def __init__(self, config):
        self.model = config['model']
        self.url = config['url']

    def generate(self, prompt: str, **kwargs):
        stream = kwargs.get("stream", False)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }

        response = requests.post(self.url, json=payload, stream=stream)

        if stream:
            return token_stream(response)
        else:
            return response.json()['response']


class OpenAIModel(BaseLLM):
    def __init__(self, config):
        self.model = config.get('model', 'o4-mini')
        self.api_key = os.environ.get(config['api_key_env'])
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message['content'].strip()

class DummyLLM(BaseLLM):
    def __init__(self, config=None):
        self.model = 'Dummy' or config['model']
        self.url = 'LocalHost' or config['url']

    def generate(self, prompt: str) -> str:
        #payload = {"model": self.model, "prompt": prompt, "stream" : False }        
        #response = requests.post(self.url, json=payload)
        return prompt


def load_llm(config):
    provider = config["provider"]
    model_config = config[provider]
    if provider == "ollama":        
        return OllamaModel(model_config)
    elif provider == "llava":
        return LlavaModel(model_config)
    elif provider == "openai":
        return OpenAIModel(model_config)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
