import json
from ...chat import Message

class CreateChatCompletion:
    def __init__(self, model, messages):
        self.model = model
        self.messages = messages
        self.temperature = 1.0
        self.top_p = 1.0
        self.n = 1
        self.stream = False
        self.stop = None
        self.presence_penalty = 0.0
        self.frequency_penalty = 0.0
        self.logit_bias = None
        self.user = None

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(data):
        return CreateChatCompletion(**json.loads(data))

class MessageChoice:
    def __init__(self, index, message, finish_reason):
        self.index = index
        self.message = Message.from_dict(message)
        self.finish_reason = finish_reason

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(data):
        obj = json.loads(data)
        return MessageChoice(
            obj['index'],
            obj['message'],  # This will be a dict that needs to be converted to a Message object
            obj['finish_reason']
        )

class ChatCompletion:
    def __init__(self, id, object, created, model, choices, usage, system_fingerprint):
        self.id = id
        self.object = object
        self.created = created
        self.model = model
        self.choices = [MessageChoice.from_json(json.dumps(choice)) for choice in choices]
        self.usage = usage
        self.system_fingerprint = system_fingerprint

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(data):
        return ChatCompletion(**json.loads(data))
