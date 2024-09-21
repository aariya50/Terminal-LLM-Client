import json
from typing import List, Optional, Dict, Any


class Thoughts:
    """
    Represents the thought process of the AI, including reasoning, plans, and criticisms.
    """

    def __init__(
        self,
        text: str,
        reasoning: Optional[str] = None,
        plan: Optional[List[str]] = None,
        criticism: Optional[str] = None,
        speak: Optional[str] = None,
    ):
        """
        Initialize a Thoughts instance.

        Args:
            text (str): The main thought text.
            reasoning (Optional[str]): The reasoning behind the thought.
            plan (Optional[List[str]]): A list of planned steps.
            criticism (Optional[str]): Self-criticism or evaluation.
            speak (Optional[str]): A spoken version of the thought.
        """
        self.text: str = text
        self.reasoning: Optional[str] = reasoning
        self.plan: Optional[List[str]] = plan
        self.criticism: Optional[str] = criticism
        self.speak: Optional[str] = speak

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Thoughts instance to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the Thoughts instance.
        """
        return {k: v for k, v in vars(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Thoughts":
        """
        Create a Thoughts instance from a dictionary.

        Args:
            data (Dict[str, Any]): A dictionary containing Thoughts data.

        Returns:
            Thoughts: A new Thoughts instance.
        """
        return cls(**data)


class Command:
    """
    Represents a command with its description and the actual command string.
    """

    def __init__(self, description: str, command: str):
        """
        Initialize a Command instance.

        Args:
            description (str): A description of what the command does.
            command (str): The actual command string to be executed.
        """
        self.description: str = description
        self.command: str = command

    def to_dict(self) -> Dict[str, str]:
        """
        Convert the Command instance to a dictionary.

        Returns:
            Dict[str, str]: A dictionary representation of the Command instance.
        """
        return vars(self)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Command":
        """
        Create a Command instance from a dictionary.

        Args:
            data (Dict[str, str]): A dictionary containing Command data.

        Returns:
            Command: A new Command instance.
        """
        return cls(**data)


class PromptResponse:
    """
    Represents the complete response from the AI, including thoughts and commands.
    """

    def __init__(self, thoughts: Thoughts, commands: List[Command]):
        """
        Initialize a PromptResponse instance.

        Args:
            thoughts (Thoughts): The AI's thoughts about the prompt.
            commands (List[Command]): A list of commands generated by the AI.
        """
        self.thoughts: Thoughts = thoughts
        self.commands: List[Command] = commands

    def empty(self) -> bool:
        """
        Check if the response contains any commands.

        Returns:
            bool: True if there are no commands, False otherwise.
        """
        return not self.commands

    @property
    def text(self) -> str:
        """Get the main thought text."""
        return self.thoughts.text

    @property
    def reasoning(self) -> Optional[str]:
        """Get the reasoning behind the thought."""
        return self.thoughts.reasoning

    @property
    def criticism(self) -> Optional[str]:
        """Get the self-criticism or evaluation."""
        return self.thoughts.criticism

    @property
    def speak(self) -> Optional[str]:
        """Get the spoken version of the thought."""
        return self.thoughts.speak

    def plan(self) -> str:
        """
        Get the plan as a string.

        Returns:
            str: The plan as a string, with steps separated by newlines if it's a list.
        """
        if isinstance(self.thoughts.plan, str):
            return self.thoughts.plan
        elif isinstance(self.thoughts.plan, list):
            return "\n".join(self.thoughts.plan)
        return ""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the PromptResponse instance to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the PromptResponse instance.
        """
        return {
            "thoughts": self.thoughts.to_dict(),
            "commands": [cmd.to_dict() for cmd in self.commands],
        }

    @classmethod
    def from_json(cls, data: str) -> "PromptResponse":
        """
        Create a PromptResponse instance from a JSON string.

        Args:
            data (str): A JSON string containing PromptResponse data.

        Returns:
            PromptResponse: A new PromptResponse instance.

        Raises:
            json.JSONDecodeError: If the input is not valid JSON.
            KeyError: If the JSON doesn't contain the expected keys.
        """
        try:
            obj = json.loads(data)
            thoughts = Thoughts.from_dict(obj["thoughts"])
            commands = [Command.from_dict(cmd) for cmd in obj["commands"]]
            return cls(thoughts, commands)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}")
        except KeyError as e:
            raise ValueError(f"Missing required key in JSON data: {e}")
