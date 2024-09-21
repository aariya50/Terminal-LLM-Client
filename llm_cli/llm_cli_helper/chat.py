from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, Any, List, Union


class Role(Enum):
    """Enum representing the roles in a conversation."""

    USER = auto()
    SYSTEM = auto()
    ASSISTANT = auto()


class Message:
    """Represents a message in a conversation."""

    def __init__(self, role: Role, content: str):
        """
        Initialize a Message object.

        Args:
            role (Role): The role of the message sender.
            content (str): The content of the message.
        """
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        """Convert the Message object to a dictionary."""
        return {"role": self.role.name.lower(), "content": self.content}

    @classmethod
    def from_dict(cls, data: Union[Dict[str, str], Any]) -> "Message":
        """
        Create a Message object from a dictionary or object.

        Args:
            data (Union[Dict[str, str], Any]): The data to create the Message from.

        Returns:
            Message: A new Message object.

        Raises:
            ValueError: If the input data is invalid.
        """
        if isinstance(data, dict):
            return cls(Role[data["role"].upper()], data["content"])
        elif hasattr(data, "role") and hasattr(data, "content"):
            return cls(Role[data.role.upper()], data.content)
        raise ValueError("Invalid input for Message.from_dict()")


class Chat(ABC):
    """Abstract base class for chat services."""

    class Error(Exception):
        """Custom exception for Chat-related errors."""

        pass

    def send(self, message: str) -> str:
        """
        Send a single message and return the response content.

        Args:
            message (str): The message to send.

        Returns:
            str: The content of the response message.

        Raises:
            Chat.Error: If there's an error during the chat process.
        """
        message_dict = Message(Role.USER, message).to_dict()
        try:
            return self.chat([message_dict]).content
        except Exception as e:
            raise self.Error(f"Error during chat: {str(e)}") from e

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> Message:
        """
        Send a list of messages and return the response.

        Args:
            messages (List[Dict[str, str]]): List of message dictionaries.

        Returns:
            Message: The response message.
        """
        pass

    @abstractmethod
    def model_id(self) -> str:
        """Return the identifier of the model being used."""
        pass

    @staticmethod
    @abstractmethod
    def requirements() -> Dict[str, Any]:
        """Return the requirements for the chat service."""
        pass

    @classmethod
    def meets_requirements(cls) -> bool:
        """Check if the current environment meets the service requirements."""
        raise NotImplementedError

    @classmethod
    def service(cls, service_name: str = "gpt") -> "Chat":
        """
        Factory method to create a Chat instance based on the service name.

        Args:
            service_name (str, optional): The name of the service to use. Defaults to "gpt".

        Returns:
            Chat: An instance of a Chat subclass.

        Raises:
            Chat.Error: If no suitable service is found or configured.
        """
        from .chat_helper import gpt, claude

        subclasses = cls.__subclasses__()
        selected = None
        if service_name:
            for subclass in subclasses:
                if subclass.requirements()["name"].lower() == service_name.lower():
                    if subclass.meets_requirements():
                        selected = subclass
                        break
            if not selected:
                raise cls.Error(
                    f"Requested service '{service_name}' is not available or does not meet requirements."
                )
        else:
            for subclass in subclasses:
                if subclass.meets_requirements():
                    selected = subclass
                    break
        if not selected:
            raise cls.Error("No LLM service is configured")

        return selected()
