"""
Core orchestrator for the chatbot framework.
Manages component registration and message flow with proper configuration and error handling.
"""
from typing import Dict, Any, Optional

from core.config import ConfigLoader
from core.errors import ComponentNotFoundError, ChatbotError, ErrorHandler
from core.context import ConversationContext


class ChatbotKernel:
    """
    Core orchestrator for the chatbot framework.
    Manages component registration and message flow.
    """

    def __init__(self, config_path=None):
        """
        Initialize the kernel with optional configuration.
        
        Args:
            config_path: Path to a configuration file (JSON or YAML)
        """
        # Initialize configuration
        self.config_loader = ConfigLoader(config_path)
        self.config = {}
        
        if config_path:
            try:
                self.config = self.config_loader.load_config()
                print(f"Configuration loaded from {config_path}")
            except Exception as e:
                # Still initialize, but with empty config
                print(f"Warning: Could not load configuration: {e}")
        
        # Initialize error handler with custom messages from config
        error_config = self.config.get('error_handling', {})
        self.error_handler = ErrorHandler(error_config)
        
        # Register custom error responses if specified in config
        if 'error_responses' in self.config:
            for error_type, response in self.config['error_responses'].items():
                self.error_handler.set_error_response(error_type, response)
        
        # Component registry
        self.components = {}
    
    def register_component(self, name: str, component: Any) -> None:
        """
        Register a component to the framework.
        
        Args:
            name: Unique identifier for the component
            component: The component instance
        """
        self.components[name] = component
        
        # Configure component if configuration exists for it
        component_config = self.config.get('components', {}).get(name)
        if component_config and hasattr(component, 'configure'):
            component.configure(component_config)
    
    def get_component(self, name: str) -> Any:
        """
        Retrieve a registered component.
        
        Args:
            name: Component identifier
            
        Returns:
            The component instance if found, None otherwise
        """
        return self.components.get(name)
    
    async def process_message(self, message: str) -> str:
        """
        Process a user message through the pipeline using ConversationContext.
        Args:
            message: User input text
        Returns:
            Response text
        """
        try:
            # Check for required components
            required_components = ['input_handler', 'nlu', 'response_generator']
            for component in required_components:
                if component not in self.components:
                    raise ComponentNotFoundError(component)
            dialog_manager = self.components.get('dialog_manager')
            # Create context object
            context = ConversationContext(input_text=message)
            # Input normalization
            context = await self.components['input_handler'].normalize(context)
            # NLU
            context = await self.components['nlu'].get_intent(context)
            # Dialog state update
            if dialog_manager:
                context = await dialog_manager.update_state(context)
                context = await dialog_manager.get_next_action(context)
                context = await self.components['response_generator'].generate(context)
                context = await dialog_manager.add_to_history(context, 'bot', context.response)
            else:
                context = await self.components['response_generator'].generate(context)
            return context.response
        except ChatbotError as e:
            debug_enabled = self.config.get('debug', False)
            if debug_enabled:
                print(f"ChatbotError: {str(e)}")
            return self.error_handler.handle_error(e)
        except Exception as e:
            debug_enabled = self.config.get('debug', False)
            if debug_enabled:
                import traceback
                traceback.print_exc()
            return self.error_handler.handle_error(e)