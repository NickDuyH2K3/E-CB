"""
Core orchestrator for the chatbot framework.
Manages component registration and message flow with proper configuration and error handling.
"""
from typing import Dict, Any, Optional

from core.config import ConfigLoader
from core.errors import ComponentNotFoundError, ChatbotError, ErrorHandler


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
    
    def process_message(self, message: str) -> str:
        """
        Process a user message through the pipeline.
        
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
                
            # Get dialog manager if available
            dialog_manager = self.components.get('dialog_manager')
            
            # Process through pipeline
            normalized_input = self.components['input_handler'].normalize(message)
            
            # Handle both SimpleNLU and SpacyNLU
            intent_result = self.components['nlu'].get_intent(normalized_input)
            
            # Update dialog state if dialog manager is available
            if dialog_manager:
                dialog_manager.update_state(intent_result, message)
                next_action = dialog_manager.get_next_action()
                response = self.components['response_generator'].generate(intent_result, next_action)
                
                # Add bot response to history
                dialog_manager.add_to_history('bot', response)
            else:
                # Extract intent name (compatible with both NLU implementations)
                intent = intent_result['name'] if isinstance(intent_result, dict) else intent_result
                response = self.components['response_generator'].generate(intent)
            
            return response
        
        except ChatbotError as e:
            # Log the error but provide user-friendly response
            debug_enabled = self.config.get('debug', False)
            if debug_enabled:
                print(f"ChatbotError: {str(e)}")
            return self.error_handler.handle_error(e)
        except Exception as e:
            # Unexpected error
            debug_enabled = self.config.get('debug', False)
            if debug_enabled:
                import traceback
                traceback.print_exc()
            return self.error_handler.handle_error(e)