

class ChatbotError(Exception):
    """Base class for all chatbot-related exceptions."""
    def __init__(self, message="An error occurred in the chatbot"):
        self.message = message
        super().__init__(self.message)


class ComponentNotFoundError(ChatbotError):
    """Exception raised when a required component is not found."""
    def __init__(self, component_name):
        self.component_name = component_name
        self.message = f"Required component '{component_name}' not found"
        super().__init__(self.message)


class IntentError(ChatbotError):
    """Exception raised when there's an issue with intent recognition."""
    def __init__(self, message="Failed to recognize intent"):
        self.message = message
        super().__init__(self.message)


class ConfigError(ChatbotError):
    """Exception raised when there's an issue with configuration."""
    def __init__(self, message="Configuration error"):
        self.message = message
        super().__init__(self.message)


class ErrorHandler:
    """Class to handle errors and provide appropriate responses."""
    
    def __init__(self, config=None):
        self.config = config or {}
        # Default error responses
        self.error_responses = {
            'ComponentNotFoundError': "I'm missing some functionality. Please contact support.",
            'IntentError': "I'm not sure what you mean.",
            'ConfigError': "I'm not configured correctly. Please contact support.",
            'default': "I encountered an error while processing your request."
        }
        
        # Override defaults with config if provided
        if config and 'error_responses' in config:
            self.error_responses.update(config['error_responses'])
    
    def set_error_response(self, error_type, response):
        """Set a custom error response for a specific error type."""
        self.error_responses[error_type] = response
        
    def handle_error(self, error):
        """
        Handle an exception and return an appropriate user-facing message.
        
        Args:
            error: The exception that was raised
            
        Returns:
            str: A user-friendly error message
        """
        if isinstance(error, ChatbotError):
            # Get the error class name without the module name
            error_type = error.__class__.__name__
            
            # Return custom response if defined
            if error_type in self.error_responses:
                return self.error_responses[error_type]
            
            # Return the error message if it's a ChatbotError
            return str(error)
        
        # For unexpected errors, return a generic message
        return self.error_responses.get('default', "An unexpected error occurred.")