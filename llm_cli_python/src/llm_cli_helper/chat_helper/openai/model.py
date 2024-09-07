import json

class Model:
    def __init__(self, id, object, owned_by):
        self.id = id
        self.object = object
        self.owned_by = owned_by

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(data):
        return Model(**json.loads(data))

class List:
    def __init__(self, object, data):
        self.object = object
        self.data = data

    @staticmethod
    def from_json(data):
        return List(**json.loads(data))

class Usage:
    def __init__(self, total_tokens, prompt_tokens, completion_tokens):
        self.total_tokens = total_tokens
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(data):
        return Usage(**json.loads(data))
