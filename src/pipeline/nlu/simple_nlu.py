from core.context import ConversationContext
from core.interfaces import NLUComponent

class SimpleNLU(NLUComponent):
    """
    Simple Natural Language Understanding component.
    Uses keyword matching for intent recognition.
    """
    
    def __init__(self):
        # Start with a rule-based approach with some basic intents
        self.patterns = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
            'farewell': ['bye', 'goodbye', 'see you', 'talk to you later'],
            'thanks': ['thank you', 'thanks', 'appreciate it'],
            'help': ['help', 'assist', 'support', 'guide me']
        }
    
    async def get_intent(self, context: ConversationContext) -> ConversationContext:
        """
        Extract intent from normalized text and update the context.
        Args:
            context: ConversationContext object
        Returns:
            Updated ConversationContext object
        """
        text = context.normalized_text
        for intent, keywords in self.patterns.items():
            if any(keyword in text for keyword in keywords):
                context.intent = {'name': intent}
                return context
        context.intent = {'name': 'unknown'}
        return context