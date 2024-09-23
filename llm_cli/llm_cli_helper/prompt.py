import re
import json
from typing import List, Union, Dict, Any
from .prompt_helper.response import PromptResponse


class Prompt:
    """
    A class to generate and manage prompts for an AI-powered CLI command constructor.

    This class handles the creation of prompts with goals and constraints,
    and provides methods to generate the final prompt and parse responses.
    """

    def __init__(self, constraints: List[str] = None):
        """
        Initialize a new Prompt instance.

        Args:
            constraints (List[str], optional): Initial list of constraints. Defaults to None.
        """
        self.constraints: List[str] = [str(c) for c in constraints or []]
        self.name: str = "Command Line Helper"
        self.description: str = (
            "an AI designed to autonomously construct and run CLI commands"
        )
        self.goals: List[str] = []

    def add_constraint(self, constraint: Union[str, List[str]]) -> None:
        """
        Add one or more constraints to the prompt.

        Args:
            constraint (Union[str, List[str]]): A single constraint or list of constraints to add.
        """
        if isinstance(constraint, list):
            self.constraints.extend(map(str, constraint))
        else:
            self.constraints.append(str(constraint))

    def add_goal(self, goal: Union[str, List[str]]) -> None:
        """
        Add one or more goals to the prompt.

        Args:
            goal (Union[str, List[str]]): A single goal or list of goals to add.
                If a string is provided, it will be split into multiple goals
                based on 'then' or period delimiters.
        """
        if isinstance(goal, list):
            self.goals.extend(goal)
        else:
            self.goals.extend(
                [g.strip() for g in re.split(r"then|\.(?:\s|$)", goal) if g.strip()]
            )

    @staticmethod
    def response_format() -> Dict[str, Any]:
        """
        Define the expected response format for the AI.

        Returns:
            Dict[str, Any]: A dictionary describing the expected response structure.
        """
        return {
            "thoughts": {
                "text": "Example thought text",
                "reasoning": "Example reasoning",
                "plan": ["Step 1", "Step 2", "Step 3"],
                "criticism": "Example criticism",
                "speak": "Example speak text",
            },
            "commands": [
                {
                    "description": "Example command description",
                    "command": "example_command",
                },
            ],
        }

    def generate(self) -> str:
        """
        Generate the final prompt string.

        Returns:
            str: The complete prompt string to be sent to the AI.
        """
        return f"""You are {self.name}, {self.description}.
        Your decisions must always be made independently without seeking user assistance. Play to your strengths as an LLM and pursue simple strategies with no legal complications.

        GOALS:

        {self._generate_list(self.goals)}
        CONSTRAINTS:

        {self._generate_list(self.constraints)}
        You should only respond in JSON format as described below
        Response Format:
        {json.dumps(self.response_format(), indent=2)}
        Ensure the response can be parsed by Python json.loads
        """

    def parse_response(self, response_json: str) -> PromptResponse:
        """
        Parse the JSON response from the AI.

        Args:
            response_json (str): The JSON string response from the AI.

        Returns:
            PromptResponse: A PromptResponse object containing the parsed response.

        Raises:
            ValueError: If the response cannot be parsed as valid JSON.
        """
        try:
            return PromptResponse.from_json(response_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")

    @staticmethod
    def _generate_list(items: List[str]) -> str:
        """
        Generate a numbered list string from a list of items.

        Args:
            items (List[str]): The list of items to format.

        Returns:
            str: A numbered list as a string.
        """
        return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
