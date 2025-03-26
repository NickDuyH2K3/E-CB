class SimpleNLU:
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
    
    def get_intent(self, text: str) -> str:
        """
        Extract intent from normalized text.
        
        Args:
            text: Normalized user input
            
        Returns:
            Intent name as string
        """
        for intent, keywords in self.patterns.items():
            if any(keyword in text for keyword in keywords):
                return intent
        return 'unknown'