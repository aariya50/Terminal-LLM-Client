import os
from ..chat import Chat
from openai import OpenAI, OpenAIError


class GPT(Chat):
    def __init__(self, model_preference="gpt-4o-mini"):
        """
        Initialize with a preferred model, defaulting to 'gpt-4o-mini'.
        Client initialization is deferred to reduce unnecessary API connections.
        """
        self._client = None
        self.model_preference = model_preference

    @classmethod
    def requirements(cls):
        """
        Provides requirements for using the GPT class.
        """
        return {
            "name": "gpt",
            "requires": ["OPENAI_API_KEY"],
            "help": "https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key",
        }

    @classmethod
    def meets_requirements(cls):
        """
        Check if the necessary API key environment variable is set.
        """
        return os.getenv("OPENAI_API_KEY") is not None

    def client(self):
        """
        Lazily creates and returns an OpenAI client instance.
        """
        if self._client is None:
            self._client = OpenAI()
        return self._client

    def model_id(self):
        """
        Fetches the list of models and returns the preferred model ID if available.
        """
        try:
            response = self.client().models.list()
            models = [model.id for model in response.data]
            return next(
                (
                    model
                    for model in [self.model_preference, "gpt-4o-mini"]
                    if model in models
                ),
                models[0],
            )
        except OpenAIError as e:
            raise RuntimeError(f"Error fetching models: {e}")

    def chat(self, messages):
        """
        Sends messages to the OpenAI API and returns the model's chat response.
        """
        try:
            response = self.client().chat.completions.create(
                model=self.model_id(), messages=messages
            )
            return response.choices[0].message
        except OpenAIError as e:
            raise RuntimeError(f"API request failed: {e}")
