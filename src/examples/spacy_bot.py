import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.kernel import ChatbotKernel
from pipeline.input_handler import InputHandler
from pipeline.nlu import SpacyNLU
from pipeline.response_generator import ResponseGenerator

def main():
    """
    Run a chatbot using the Spacy-enhanced NLU.
    """
    # Initialize the chatbot kernel
    kernel = ChatbotKernel()
    
    # Create NLU with custom intents
    nlu = SpacyNLU()
    
    # Add some custom intents to demonstrate flexibility
    nlu.add_custom_intent(
        'tech_support', 
        keywords=['computer', 'software', 'tech', 'problem'], 
        patterns=['I have a technical issue', 'my computer is not working']
    )
    nlu.add_custom_intent(
        'weather_inquiry', 
        keywords=['weather', 'temperature', 'forecast'], 
        patterns=['What\'s the weather like', 'temperature today']
    )
    
    # Register components
    kernel.register_component('input_handler', InputHandler())
    kernel.register_component('nlu', nlu)
    kernel.register_component('response_generator', ResponseGenerator())
    
    # Enhanced interaction loop with intent and entity display
    print("Advanced Spacy NLU Chatbot Demo")
    print("Type 'exit' to end the conversation.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("You: ")
            
            # Exit conditions
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Bot: Goodbye!")
                break
            
            # Process message and get response
            response = kernel.process_message(user_input)
            
            # Get intent details for demonstration
            intent_details = kernel.get_component('nlu').get_intent(user_input)
            
            # Print detailed intent information
            print(f"\n[Intent Analysis]")
            print(f"Recognized Intent: {intent_details['name']} (Confidence: {intent_details['confidence']*100:.2f}%)")
            
            # Print extracted entities
            if intent_details['entities']:
                print("Extracted Entities:")
                for entity_type, entities in intent_details['entities'].items():
                    if entities:  # Only print if there are entities
                        print(f"  - {entity_type}: {', '.join(entities)}")
            
            # Print bot response
            print(f"Bot: {response}\n")
        
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()