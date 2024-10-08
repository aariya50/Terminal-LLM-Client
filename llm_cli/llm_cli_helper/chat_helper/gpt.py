import os
from typing import Dict, List, Optional
from openai import OpenAI, OpenAIError
from ..chat import Chat


class GPT(Chat):
    """
    A class to interact with the GPT AI model using the OpenAI API.

    This class provides methods to initialize the GPT client, check requirements,
    and send chat messages to the GPT model.
    """

    # Default model for GPT API
    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, model_preference: str = DEFAULT_MODEL):
        """
        Initialize the GPT chat instance.

        Args:
            model_preference (str): Preferred model ID. Defaults to DEFAULT_MODEL.
        """
        self._client: Optional[OpenAI] = None
        self.model_preference: str = model_preference

    @classmethod
    def requirements(cls) -> Dict[str, str]:
        """
        Specify the requirements for using GPT.

        Returns:
            Dict[str, str]: Dictionary containing name, required environment variables, and help link.
        """
        return {
            "name": "gpt",
            "requires": ["OPENAI_API_KEY"],
            "help": "https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key",
        }

    @classmethod
    def meets_requirements(cls) -> bool:
        """
        Check if the required API key is set in the environment.

        Returns:
            bool: True if the API key is set, False otherwise.
        """
        return os.getenv("OPENAI_API_KEY") is not None

    def client(self) -> OpenAI:
        """
        Get or create an OpenAI client instance.

        Returns:
            OpenAI: OpenAI client instance.
        """
        if self._client is None:
            self._client = OpenAI()
        return self._client

    def model_id(self) -> str:
        """
        Get the model ID to use for chat completions.
        Attempts to use the preferred model, falls back to DEFAULT_MODEL or the first available model.

        Returns:
            str: Model ID string.

        Raises:
            RuntimeError: If there's an error fetching the models.
        """
        try:
            response = self.client().models.list()
            models = [model.id for model in response.data]
            return next(
                (
                    model
                    for model in [self.model_preference, self.DEFAULT_MODEL]
                    if model in models
                ),
                models[0],
            )
        except OpenAIError as e:
            raise RuntimeError(f"Error fetching models: {e}")

    def chat(self, messages: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Send a chat request to the GPT API and return the response.

        Args:
            messages (List[Dict[str, str]]): List of message dictionaries.

        Returns:
            Dict[str, str]: Response message from GPT.

        Raises:
            RuntimeError: If the API request fails.
        """
        try:
            response = self.client().chat.completions.create(
                model=self.model_id(), messages=messages
            )
            return response.choices[0].message
        except OpenAIError as e:
            raise RuntimeError(f"API request failed: {e}")
