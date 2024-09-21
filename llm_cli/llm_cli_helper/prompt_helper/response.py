import json

class Thoughts:
    def __init__(self, text, reasoning=None, plan=None, criticism=None, speak=None):
        self.text = text
        self.reasoning = reasoning
        self.plan = plan
        self.criticism = criticism
        self.speak = speak

    def to_dict(self):
        return {k: v for k, v in vars(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Command:
    def __init__(self, description, command):
        self.description = description
        self.command = command

    def to_dict(self):
        return vars(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class PromptResponse:
    def __init__(self, thoughts, commands):
        self.thoughts = thoughts
        self.commands = commands

    def empty(self):
        return not self.commands

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
        if isinstance(self.thoughts.plan, str):
            return self.thoughts.plan
        elif isinstance(self.thoughts.plan, list):
            return "\n".join(self.thoughts.plan)
        return ""

    def to_dict(self):
        return {
            "thoughts": self.thoughts.to_dict(),
            "commands": [cmd.to_dict() for cmd in self.commands]
        }

    @classmethod
    def from_json(cls, data):
        obj = json.loads(data)
        thoughts = Thoughts.from_dict(obj['thoughts'])
        commands = [Command.from_dict(cmd) for cmd in obj['commands']]
        return cls(thoughts, commands)