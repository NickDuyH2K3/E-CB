from typing import Dict, Any, List, Optional
from core.context import ConversationContext
from core.interfaces import DialogManagerComponent
import yaml

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

class DialogManager(DialogManagerComponent):
    """
    Manages the conversation flow and state.
    """
    
    def __init__(self):
        self.state = DialogState()
        self.flows = {}
    
    async def update_state(self, context: ConversationContext) -> ConversationContext:
        """
        Update the dialog state in the context based on latest interaction.
        Args:
            context: ConversationContext object
        Returns:
            Updated ConversationContext object
        """
        state = context.dialog_state
        state['previous_intent'] = state.get('current_intent')
        state['current_intent'] = context.intent.get('name') if isinstance(context.intent, dict) else context.intent
        # Update entities if available
        if isinstance(context.intent, dict) and 'entities' in context.intent:
            if 'entities' not in state:
                state['entities'] = {}
            for entity_type, values in context.intent['entities'].items():
                if entity_type not in state['entities']:
                    state['entities'][entity_type] = []
                state['entities'][entity_type].extend(values)
        # Add to conversation history
        context.history.append({
            'role': 'user',
            'content': context.input_text,
            'turn': state.get('turn_count', 0)
        })
        # Increment turn counter
        state['turn_count'] = state.get('turn_count', 0) + 1
        context.dialog_state = state
        return context
    
    def register_flow(self, name: str, flow_definition: Dict[str, Any]) -> None:
        """
        Register a conversation flow.
        
        Args:
            name: Flow identifier
            flow_definition: Dictionary defining the flow structure
        """
        self.flows[name] = flow_definition
    
    async def get_next_action(self, context: ConversationContext) -> ConversationContext:
        """
        Determine the next action based on current state and update context.
        Args:
            context: ConversationContext object
        Returns:
            Updated ConversationContext object with next action info in dialog_state
        """
        state = context.dialog_state
        # Check if we're in an active flow
        if state.get('active_flow') and hasattr(self, 'flows') and state['active_flow'] in self.flows:
            flow = self.flows[state['active_flow']]
            current_step = state.get('flow_step')
            if current_step in flow and 'next' in flow[current_step]:
                next_step = flow[current_step]['next']
                state['flow_step'] = next_step
                state['next_action'] = {
                    'type': 'flow_step',
                    'flow': state['active_flow'],
                    'step': next_step,
                    'action': flow[next_step].get('action', {})
                }
                context.dialog_state = state
                return context
        # Default action based on intent
        state['next_action'] = {
            'type': 'intent_response',
            'intent': state.get('current_intent')
        }
        context.dialog_state = state
        return context
    
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
    
    async def add_to_history(self, context: ConversationContext, role: str, content: str) -> ConversationContext:
        """
        Add a message to conversation history in the context.
        Args:
            context: ConversationContext object
            role: Message role ('user', 'bot')
            content: Message content
        Returns:
            Updated ConversationContext object
        """
        state = context.dialog_state
        context.history.append({
            'role': role,
            'content': content,
            'turn': state.get('turn_count', 0)
        })
        return context
    
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

    def load_flows_from_yaml(self, yaml_path: str) -> None:
        """
        Load dialog flows from a YAML file and register them.
        Args:
            yaml_path: Path to the YAML file containing dialog flows
        """
        with open(yaml_path, 'r', encoding='utf-8') as f:
            flows = yaml.safe_load(f)
            for name, flow in flows.items():
                self.register_flow(name, flow)