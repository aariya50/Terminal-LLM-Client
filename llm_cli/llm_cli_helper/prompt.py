import re
import json
from .prompt_helper.response import PromptResponse

class Prompt:
    def __init__(self, constraints=None):
        self.constraints = [str(c) for c in constraints or []]
        self.name = "Command Line Helper"
        self.description = "an AI designed to autonomously construct and run CLI commands"
        self.goals = []

    def add_constraint(self, constraint):
        if isinstance(constraint, list):
            self.constraints.extend(constraint)
        else:
            self.constraints.append(constraint)

    def add_goal(self, goal):
        if isinstance(goal, list):
            self.goals.extend(goal)
        else:
            self.goals.extend([g.strip() for g in re.split(r"then|\\.\\s", goal) if g.strip()])

    def response_format(self):
        return {
            "thoughts": {
                "text": "thought",
                "reasoning": "reasoning",
                "plan": ["- short bulleted", "- list that conveys", "- long-term plan"],
                "criticism": "constructive self-criticism",
                "speak": "thoughts summary to say to user",
            },
            "commands": [
                {
                    "description": "description of what this command does",
                    "command": "command parameter {parameter placeholder}",
                },
            ],
        }

    def generate(self):
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

    def parse_response(self, response_json):
        return PromptResponse.from_json(response_json)

    @staticmethod
    def _generate_list(items):
        return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
