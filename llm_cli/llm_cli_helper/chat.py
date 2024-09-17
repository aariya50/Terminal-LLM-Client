import json
import os
# from llm_cli_helper.chat_helper.gpt import GPT
from abc import ABC, abstractmethod

class Role:
    User = "user"
    System = "system"
    Assistant = "assistant"

class Message:
    def __init__(self, role, content, refusal):
        self.role = role
        self.content = content
        self.refusal = refusal
        
    def to_dict(self):
        """Convert the Message instance to a dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "refusal": self.refusal
        }
    def from_dict(data):
        """Create a Message instance from a dictionary."""
        return Message(**data)
        
    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(data):
        return Message(**json.loads(data))

class Chat(ABC):
    class Error(Exception):
        pass

    Requirements = dict(
        name=str,
        requires=list,
        optional=list,
        help=str
    )

    def __init__(self):
        self.model_preference = ""

    def send(self, message):
        message_dict = Message(Role.User, message, None).to_dict()
        return self.chat([message_dict]).content

    @abstractmethod
    def chat(self, message):
        pass

    @abstractmethod
    def model_id(self):
        pass

    @classmethod
    def service(cls, service_name="gpt"):
        from .chat_helper.gpt import GPT
        from .chat_helper.claude import Claude
        
        subclasses = cls.__subclasses__()
        selected = None
        if service_name:
            for subclass in subclasses:
                if subclass.requirements()["name"].lower() == service_name.lower():
                    if subclass.meets_requirements():
                        selected = subclass
                        break
            if not selected:
                raise cls.Error(f"Requested service '{service_name}' is not available or does not meet requirements.")
        else:
            for subclass in subclasses:
                if subclass.meets_requirements():
                    selected = subclass
                    break
        # Instantiate the selected subclass, specifically handling GPT's required arguments
        if not selected:
            raise cls.Error("No LLM service is configured")

        # Instantiate the selected subclass with required parameters
        return selected()

    @classmethod
    def requirements(cls):
        requirements = []
        for subclass in cls.__subclasses__():
            requirements.append(subclass.requirements())
        return requirements
