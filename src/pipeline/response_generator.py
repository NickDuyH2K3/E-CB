import random
from typing import Dict, List

class ResponseGenerator:
    """
    Generates responses based on recognized intent.
    """
    
    def __init__(self):
        self.templates: Dict[str, List[str]] = {
            'greeting': [
                'Hello there!',
                'Hi! How can I help you today?',
                'Greetings! How may I assist you?'
            ],
            'farewell': [
                'Goodbye!',
                'See you later!',
                'Have a great day!'
            ],
            'thanks': [
                'You\'re welcome!',
                'Happy to help!',
                'Anytime!'
            ],
            'help': [
                'I can help you with various tasks. Just tell me what you need!',
                'What kind of assistance do you need?',
                'I\'m here to help. What would you like to know?'
            ],
            'unknown': [
                'I\'m not sure I understand. Could you rephrase that?',
                'I don\'t quite get what you mean.',
                'Could you be more specific?'
            ]
        }
    
    def generate(self, intent: str) -> str:
        """
        Generate a response based on intent.
        
        Args:
            intent: Recognized intent
            
        Returns:
            Response text
        """
        responses = self.templates.get(intent, self.templates['unknown'])
        return random.choice(responses)