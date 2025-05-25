from core.context import ConversationContext
from core.interfaces import InputHandlerComponent

class InputHandler(InputHandlerComponent):
    """
    Handles preprocessing of user input.
    """
    
    async def normalize(self, context: ConversationContext) -> ConversationContext:
        """
        Normalize input text and update the context.
        
        Args:
            context: ConversationContext object
        
        Returns:
            Updated ConversationContext object
        """
        # Lowercase and remove extra whitespace
        context.normalized_text = context.input_text.lower().strip()
        return context