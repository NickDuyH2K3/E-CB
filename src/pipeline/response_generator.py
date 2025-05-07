# src/pipeline/response_generator.py (updated)
import random
from typing import Union, Dict, Any, Optional

class ResponseGenerator:
    """
    Generates responses based on recognized intent and dialog state.
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
            ],
            'tech_support': [
                'I can help with your technical issue. What problem are you experiencing?',
                'For tech support, I need more details about your problem.',
                'Tech support ready to assist! What seems to be the issue?'
            ],
            'weather_inquiry': [
                'I don\'t have real-time weather data, but I can discuss weather topics.',
                'Weather information is not in my current capabilities.',
                'I can help you understand weather concepts, but can\'t provide forecasts.'
            ],
            'follow_up': [
                'Is there anything else you\'d like to know about that?',
                'Do you have any follow-up questions?',
                'Would you like more information on this topic?'
            ]
        }
        
        # Flow-specific responses
        self.flow_responses = {
            'onboarding': {
                'start': 'Let\'s get you set up! First, what would you like me to call you?',
                'get_name': 'Nice to meet you, {name}! What can I help you with today?',
                'explain_features': 'I can help with various tasks like answering questions and providing information.'
            }
        }
    
    def generate(self, intent: Union[str, Dict[str, Any]], dialog_state: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response based on intent and dialog state.
        
        Args:
            intent: Recognized intent (string or dictionary)
            dialog_state: Optional dialog state information
            
        Returns:
            Response text
        """
        # Extract intent name if it's a dictionary
        intent_name = intent['name'] if isinstance(intent, dict) else intent
        
        # Check for flow-specific responses
        if dialog_state and dialog_state.get('type') == 'flow_step':
            flow = dialog_state.get('flow')
            step = dialog_state.get('step')
            
            if flow in self.flow_responses and step in self.flow_responses[flow]:
                response_template = self.flow_responses[flow][step]
                
                # Handle template variables
                if '{' in response_template and dialog_state.get('context'):
                    context = dialog_state.get('context', {})
                    for key, value in context.items():
                        response_template = response_template.replace(f'{{{key}}}', str(value))
                
                return response_template
        
        # Extract entities for response personalization if available
        entities = {}
        if isinstance(intent, dict) and 'entities' in intent:
            entities = intent['entities']
        
        # Get appropriate response template
        responses = self.templates.get(intent_name, self.templates['unknown'])
        base_response = random.choice(responses)
        
        # Personalize response if possible
        personalized_response = self._personalize_response(base_response, entities)
        
        return personalized_response
    
    def _personalize_response(self, response: str, entities: Dict[str, Any]) -> str:
        """
        Personalize response with entity information.
        
        Args:
            response: Base response template
            entities: Extracted entities
            
        Returns:
            Personalized response
        """
        # Example: If there's a person entity, use it in the response
        if 'PERSON' in entities and entities['PERSON'] and '{person}' in response:
            response = response.replace('{person}', entities['PERSON'][0])
        
        return response
    
    def add_response_template(self, intent: str, templates: list) -> None:
        """
        Add or update response templates for an intent.
        
        Args:
            intent: Intent name
            templates: List of response templates
        """
        self.templates[intent] = templates
    
    def add_flow_responses(self, flow_name: str, responses: Dict[str, str]) -> None:
        """
        Add responses for a dialog flow.
        
        Args:
            flow_name: Flow identifier
            responses: Dictionary mapping flow steps to response templates
        """
        self.flow_responses[flow_name] = responses