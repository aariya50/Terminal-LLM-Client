import os
import requests
import json
from ..chat import Chat
from .openai.chat_completion import CreateChatCompletion, ChatCompletion
from anthropic import Anthropic

class Claude(Chat):
    @classmethod
    def requirements(cls):
        return {
            "name": "claude",
            "requires": ["ANTHROPIC_API_KEY"],
            "help": "https://support.anthropic.com/en/articles/8114521-how-can-i-access-the-anthropic-api"
        }

    @classmethod
    def meets_requirements(cls):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        return api_key is not None

    def __init__(self, key):
        self.key = key

    def client(self):
        return Anthropic(api_key=self.key)

    def model_id(self):
        return "claude-3-haiku-20240307"

    def chat(self, messages):
        client = self.client()
        response = client.messages.create(
            model=self.model_id(),
            max_tokens=1024,
            messages=[
                {"role": "user", "content": "Hello, Claude"}
            ]
        )
        print(response)
        # if not response.ok:
        #     raise Exception(f"Unexpected response {response.status_code}\n{response.text}")
        # chat = ChatCompletion.from_json(response.text)
        
        return response.content[0].text
