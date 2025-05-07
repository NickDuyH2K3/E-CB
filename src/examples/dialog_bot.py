# src/examples/dialog_bot.py
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.kernel import ChatbotKernel
from pipeline.input_handler import InputHandler
from pipeline.nlu import SpacyNLU
from pipeline.response_generator import ResponseGenerator
from pipeline.dialog_manager import DialogManager

def main():
    """
    Run a chatbot using the dialog manager for state tracking.
    """
    # Initialize the chatbot kernel
    kernel = ChatbotKernel()
    
    # Create components
    input_handler = InputHandler()
    nlu = SpacyNLU()
    response_generator = ResponseGenerator()
    dialog_manager = DialogManager()
    
    # Add some custom intents
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
    
    # Register a dialog flow
    onboarding_flow = {
        'start': {
            'next': 'get_name',
            'action': 'prompt_name'
        },
        'get_name': {
            'next': 'explain_features',
            'action': 'store_name'
        },
        'explain_features': {
            'next': 'end',
            'action': 'list_features'
        },
        'end': {
            'action': 'end_flow'
        }
    }
    dialog_manager.register_flow('onboarding', onboarding_flow)
    
    # Register components to kernel
    kernel.register_component('input_handler', input_handler)
    kernel.register_component('nlu', nlu)
    kernel.register_component('response_generator', response_generator)
    kernel.register_component('dialog_manager', dialog_manager)
    
    # Enhanced interaction loop
    print("Dialog-Aware Chatbot Demo")
    print("Type 'exit' to end the conversation or 'start onboarding' to try the dialog flow.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("You: ")
            
            # Exit conditions
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Bot: Goodbye!")
                break
            
            # Special command to start onboarding flow
            if user_input.lower() == 'start onboarding':
                dialog_manager.start_flow('onboarding')
                print(f"Bot: {response_generator.flow_responses['onboarding']['start']}")
                continue
            
            # Process message and get response
            response = kernel.process_message(user_input)
            
            # Print bot response
            print(f"Bot: {response}")
            
            # Optional: Show dialog state (for debugging)
            if '--debug' in sys.argv:
                state = dialog_manager.state
                print(f"\n[Dialog State]")
                print(f"Current Intent: {state.current_intent}")
                print(f"Turn Count: {state.turn_count}")
                if state.active_flow:
                    print(f"Active Flow: {state.active_flow} (Step: {state.context.get('flow_step', 'none')})")
                print()
        
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()