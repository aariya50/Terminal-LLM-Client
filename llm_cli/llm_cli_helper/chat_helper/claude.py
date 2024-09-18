import os
from typing import Dict, List, Optional
from anthropic import Anthropic
from ..chat import Chat

class Claude(Chat):
    # Default model for Claude API
    DEFAULT_MODEL = "claude-3-haiku-20240307"

    def __init__(self, model_preference: str = DEFAULT_MODEL):
        """
        Initialize the Claude chat instance.
        
        :param model_preference: Preferred model ID, defaults to DEFAULT_MODEL
        """
        self._client: Optional[Anthropic] = None
        self.model_preference = model_preference

    @classmethod
    def requirements(cls) -> Dict[str, str]:
        """
        Specify the requirements for using Claude.
        
        :return: Dictionary containing name, required environment variables, and help link
        """
        return {
            "name": "claude",
            "requires": ["ANTHROPIC_API_KEY"],
            "help": "https://support.anthropic.com/en/articles/8114521-how-can-i-access-the-anthropic-api"
        }

    @classmethod
    def meets_requirements(cls) -> bool:
        """
        Check if the required API key is set in the environment.
        
        :return: True if the API key is set, False otherwise
        """
        return os.getenv("ANTHROPIC_API_KEY") is not None

    def client(self) -> Anthropic:
        """
        Get or create an Anthropic client instance.
        
        :return: Anthropic client instance
        """
        if self._client is None:
            self._client = Anthropic()
        return self._client

    def model_id(self) -> str:
        """
        Get the model ID to use for chat completions.
        
        :return: Model ID string
        """
        return self.DEFAULT_MODEL

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Send a chat request to the Claude API and return the response.
        
        :param messages: List of message dictionaries
        :return: Response text from Claude
        :raises ValueError: If no response content is received
        """
        client = self.client()
        response = client.messages.create(
            model=self.model_id(),
            max_tokens=1024,
            messages=messages
        )
        
        if not response.content:
            raise ValueError("No response received from Claude API")
        
        return response.content[0].text
