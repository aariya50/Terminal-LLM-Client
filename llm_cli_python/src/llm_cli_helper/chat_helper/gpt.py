import os
import requests
import json
from ..chat import Chat
from .openai.chat_completion import CreateChatCompletion, ChatCompletion

class GPT(Chat):
    @classmethod
    def requirements(cls):
        return {
            "name": "OpenAI GPT",
            "requires": ["OPENAI_API_KEY"],
            "optional": ["OPENAI_API_ORG"],
            "help": "https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key"
        }

    @classmethod
    def meets_requirements(cls):
        api_key = os.getenv("OPENAI_API_KEY")
        return api_key is not None

    def __init__(self, openai_key, openai_org=None):
        self.openai_key = openai_key
        self.openai_org = openai_org

    def client(self):
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        if self.openai_org:
            headers["OpenAI-Organization"] = self.openai_org
        return requests.Session(), headers

    def model_id(self):
        session, headers = self.client()
        response = session.get("https://api.openai.com/v1/models", headers=headers)
        models = [model["id"] for model in response.json()["data"]]
        preferred = [self.model_preference, "gpt-4", "gpt-3.5-turbo"]
        
        for model in preferred:
            if model and model in models:
                return model
        return preferred[-1]

    def chat(self, messages):
        session, headers = self.client()

        chat_completion = CreateChatCompletion(self.model_id(), messages)
        
        response = session.post("https://api.openai.com/v1/chat/completions", json=chat_completion.__dict__, headers=headers)
        if not response.ok:
            raise Exception(f"Unexpected response {response.status_code}\n{response.text}")
        chat = ChatCompletion.from_json(response.text)
        
        return chat.choices[0].message
