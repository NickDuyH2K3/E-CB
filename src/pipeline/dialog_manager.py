from typing import Dict, Any, List, Optional

HISTORY_LIMIT = 3
TURN_INCREMENT = 1

class DialogState:
    """
    Class to store dialog state information.
    """
    def __init__(self):
        self.current_intent = None
        self.previous_intent = None
        self.context = {}
        self.entities = {}
        self.conversation_history = []
        self.turn_count = 0
        self.active_flow = None

class DialogManager:
    """
    Manages the conversation flow and state.
    """
    
    def __init__(self):
        self.state = DialogState()
        self.flows = {}
    
    def update_state(self, intent: Dict[str, Any], user_input: str) -> None:
        """
        Update the dialog state based on latest interaction.
        
        Args:
            intent: Intent recognition result
            user_input: Original user input
        """
        # Store previous intent
        self.state.previous_intent = self.state.current_intent
        
        # Update current intent
        self.state.current_intent = intent.get('name') if isinstance(intent, dict) else intent
        
        # Update entities if available
        if isinstance(intent, dict) and 'entities' in intent:
            for entity_type, values in intent['entities'].items():
                if entity_type not in self.state.entities:
                    self.state.entities[entity_type] = []
                self.state.entities[entity_type].extend(values)
        
        # Add to conversation history
        self.state.conversation_history.append({
            'role': 'user',
            'content': user_input,
            'turn': self.state.turn_count
        })
        
        # Increment turn counter
        self.state.turn_count += TURN_INCREMENT
    
    def register_flow(self, name: str, flow_definition: Dict[str, Any]) -> None:
        """
        Register a conversation flow.
        
        Args:
            name: Flow identifier
            flow_definition: Dictionary defining the flow structure
        """
        self.flows[name] = flow_definition
    
    def get_next_action(self) -> Dict[str, Any]:
        """
        Determine the next action based on current state.
        
        Returns:
            Dictionary with next action information
        """
        # Check if we're in an active flow
        if self.state.active_flow and self.state.active_flow in self.flows:
            flow = self.flows[self.state.active_flow]
            current_step = self.state.context.get('flow_step')
            
            # Check if there's a next step in the flow
            if current_step in flow and 'next' in flow[current_step]:
                next_step = flow[current_step]['next']
                
                # Update the flow step
                self.state.context['flow_step'] = next_step
                
                # Return action for the next step
                return {
                    'type': 'flow_step',
                    'flow': self.state.active_flow,
                    'step': next_step,
                    'action': flow[next_step].get('action', {})
                }
        
        # Default action based on intent
        return {
            'type': 'intent_response',
            'intent': self.state.current_intent
        }
    
    def start_flow(self, flow_name: str) -> bool:
        """
        Start a predefined conversation flow.
        
        Args:
            flow_name: Name of the flow to start
            
        Returns:
            Success status
        """
        if flow_name in self.flows:
            self.state.active_flow = flow_name
            self.state.context['flow_step'] = 'start'
            return True
        return False
    
    def end_flow(self) -> None:
        """
        End the current flow.
        """
        self.state.active_flow = None
        if 'flow_step' in self.state.context:
            del self.state.context['flow_step']
    
    def add_to_history(self, role: str, content: str) -> None:
        """
        Add a message to conversation history.
        
        Args:
            role: Message role ('user', 'bot')
            content: Message content
        """
        self.state.conversation_history.append({
            'role': role,
            'content': content,
            'turn': self.state.turn_count
        })
    
    def get_context_for_intent(self, intent_name: str) -> Dict[str, Any]:
        """
        Get relevant context for a specific intent.
        
        Args:
            intent_name: Target intent
            
        Returns:
            Context information relevant to the intent
        """
        context = {
            'entities': self.state.entities,
            'turn_count': self.state.turn_count,
            'previous_intent': self.state.previous_intent
        }
        
        # Add any additional context specific to the intent
        if intent_name in ['follow_up', 'clarification']:
            # Include recent conversation history for these intents
            context['recent_history'] = self.state.conversation_history[-HISTORY_LIMIT:] if len(self.state.conversation_history) > HISTORY_LIMIT else self.state.conversation_history
        
        return context