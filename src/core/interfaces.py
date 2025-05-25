from abc import ABC, abstractmethod
from core.context import ConversationContext

class NLUComponent(ABC):
    @abstractmethod
    async def get_intent(self, context: ConversationContext) -> ConversationContext:
        pass

class ResponseGeneratorComponent(ABC):
    @abstractmethod
    async def generate(self, context: ConversationContext) -> ConversationContext:
        pass

class InputHandlerComponent(ABC):
    @abstractmethod
    async def normalize(self, context: ConversationContext) -> ConversationContext:
        pass

class DialogManagerComponent(ABC):
    @abstractmethod
    async def update_state(self, context: ConversationContext) -> ConversationContext:
        pass

    @abstractmethod
    async def get_next_action(self, context: ConversationContext) -> ConversationContext:
        pass

    @abstractmethod
    async def add_to_history(self, context: ConversationContext, speaker: str, message: str) -> ConversationContext:
        pass 