from abc import ABC, abstractmethod

class Role:
    User = "user"
    System = "system"
    Assistant = "assistant"

class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content
        
    def to_dict(self):
        """Convert the Message instance to a dictionary."""
        return {
            "role": self.role,
            "content": self.content
        }

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, dict):
            return cls(data.get('role'), data.get('content'))
        elif hasattr(data, 'role') and hasattr(data, 'content'):
            return cls(data.role, data.content)
        else:
            raise ValueError("Invalid input for Message.from_dict()")

class Chat(ABC):
    class Error(Exception):
        pass

    def __init__(self):
        pass

    def send(self, message):
        message_dict = Message(Role.User, message).to_dict()
        return self.chat([message_dict]).content

    @abstractmethod
    def chat(self, message):
        pass

    @abstractmethod
    def model_id(self):
        pass

    @staticmethod
    @abstractmethod
    def requirements():
        pass

    @classmethod
    def service(cls, service_name="gpt"):
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
                raise cls.Error(f"Requested service '{service_name}' is not available or does not meet requirements.")
        else:
            for subclass in subclasses:
                if subclass.meets_requirements():
                    selected = subclass
                    break
        if not selected:
            raise cls.Error("No LLM service is configured")

        return selected()