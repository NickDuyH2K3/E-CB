class InputHandler:
    """
    Handles preprocessing of user input.
    """
    
    def normalize(self, text: str) -> str:
        """
        Normalize input text.
        
        Args:
            text: Raw user input
            
        Returns:
            Normalized text
        """
        # Start with basic processing
        # Lowercase and remove extra whitespace
        return text.lower().strip()