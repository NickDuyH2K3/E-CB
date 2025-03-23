import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.kernel import ChatbotKernel
from pipeline.input_handler import InputHandler
from pipeline.nlu import SimpleNLU
from pipeline.response_generator import ResponseGenerator

def main():
    """
    Run a simple chatbot using the framework.
    """
    # Initialize the chatbot kernel
    kernel = ChatbotKernel()
    
    # Register required components
    kernel.register_component('input_handler', InputHandler())
    kernel.register_component('nlu', SimpleNLU())
    kernel.register_component('response_generator', ResponseGenerator())
    
    # Simple interaction loop
    print("Simple Chatbot Framework Demo")
    print("Type 'exit' to end the conversation.")
    print("-" * 50)
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Bot: Goodbye!")
            break
        
        response = kernel.process_message(user_input)
        print(f"Bot: {response}")

if __name__ == "__main__":
    main()