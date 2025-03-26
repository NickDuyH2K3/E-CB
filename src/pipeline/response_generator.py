import random
from typing import Union, Dict, Any

class ResponseGenerator:
    """
    Generates responses based on recognized intent.
    """
    
    def __init__(self):
        self.templates = {
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
            'help_request': [
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
    
    def generate(self, intent: Union[str, Dict[str, Any]]) -> str:
        """
        Generate a response based on intent.
        
        Args:
            intent: Recognized intent (string or dictionary)
            
        Returns:
            Response text
        """
        # Extract intent name if it's a dictionary
        intent_name = intent['name'] if isinstance(intent, dict) else intent
        
        # Get appropriate response template
        responses = self.templates.get(intent_name, self.templates['unknown'])
        return random.choice(responses)