import json

class Thoughts:
    def __init__(self, text, reasoning=None, plan=None, criticism=None, speak=None):
        self.text = text
        self.reasoning = reasoning
        self.plan = plan
        self.criticism = criticism
        self.speak = speak

    def to_dict(self):
        return {
            "text": self.text,
            "reasoning": self.reasoning,
            "plan": self.plan,
            "criticism": self.criticism,
            "speak": self.speak
        }

    @staticmethod
    def from_dict(data):
        return Thoughts(**data)

class Command:
    def __init__(self, description, command):
        self.description = description
        self.command = command

    def to_dict(self):
        return {
            "description": self.description,
            "command": self.command
        }

    @staticmethod
    def from_dict(data):
        return Command(**data)

class PromptResponse:
    def __init__(self, thoughts, commands):
        self.thoughts = thoughts
        self.commands = commands

    def empty(self):
        return len(self.commands) == 0

    @property
    def text(self):
        return self.thoughts.text

    @property
    def reasoning(self):
        return self.thoughts.reasoning

    @property
    def criticism(self):
        return self.thoughts.criticism

    @property
    def speak(self):
        return self.thoughts.speak

    def plan(self):
        plan = self.thoughts.plan
        if isinstance(plan, str):
            points = [plan]
        elif isinstance(plan, list):
            points = plan
        else:
            points = []
        return "\n".join(points)

    def to_dict(self):
        return {
            "thoughts": self.thoughts.to_dict(),
            "commands": [cmd.to_dict() for cmd in self.commands]
        }

    @staticmethod
    def from_json(data):
        obj = json.loads(data)
        thoughts = Thoughts.from_dict(obj['thoughts'])
        commands = [Command.from_dict(cmd) for cmd in obj['commands']]
        return PromptResponse(thoughts, commands)