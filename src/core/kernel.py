from typing import Dict, Any, Optional

class ChatbotKernel:
    """
    Core orchestrator for the chatbot framework.
    Manages component registration and message flow.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.components = {}
    
    def register_component(self, name: str, component: Any) -> None:
        """
        Register a component to the framework.
        
        Args:
            name: Unique identifier for the component
            component: The component instance
        """
        self.components[name] = component
    
    def get_component(self, name: str) -> Any:
        """
        Retrieve a registered component.
        
        Args:
            name: Component identifier
            
        Returns:
            The component instance if found, None otherwise
        """
        return self.components.get(name, None)
    
    def process_message(self, message: str) -> str:
        """
        Process a user message through the pipeline.
        
        Args:
            message: User input text
            
        Returns:
            Response text
        """
        # Basic pipeline implementation
        if 'input_handler' not in self.components:
            raise ValueError("Required component 'input_handler' not registered")
        if 'nlu' not in self.components:
            raise ValueError("Required component 'nlu' not registered")
        if 'response_generator' not in self.components:
            raise ValueError("Required component 'response_generator' not registered")
            
        # Process through pipeline
        normalized_input = self.components['input_handler'].normalize(message)
        intent = self.components['nlu'].get_intent(normalized_input)
        response = self.components['response_generator'].generate(intent)
        
        return response