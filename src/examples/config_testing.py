"""
Example chatbot that uses configuration files for setup.
This bot demonstrates proper usage of ConfigLoader and ErrorHandler.
"""
import sys
import os
import json
import yaml

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.kernel import ChatbotKernel
from core.config import ConfigLoader
from core.errors import ChatbotError
from pipeline.input_handler import InputHandler
from pipeline.nlu import SimpleNLU, SpacyNLU
from pipeline.response_generator import ResponseGenerator
from pipeline.dialog_manager import DialogManager


def create_example_config(config_path):
    """Create an example configuration file if it doesn't exist."""
    # Check if file already exists
    if os.path.exists(config_path):
        return
    
    # Create config directory if needed
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    
    # Create example configuration
    example_config = {
        "name": "Config Bot",
        "description": "A bot configured using a JSON file",
        "debug": True,
        "error_responses": {
            "IntentError": "I don't understand what you mean. Can you try different words?",
            "ComponentNotFoundError": "I'm not fully set up yet. Please try again later.",
            "default": "Sorry, something went wrong."
        },
        "components": {
            "nlu": {
                "type": "simple",
                "intents": {
                    "greeting": ["hello", "hi", "hey", "good morning", "good afternoon"],
                    "farewell": ["bye", "goodbye", "see you later", "exit", "quit"],
                    "help": ["help", "assist", "support", "guide", "instructions"],
                    "info": ["what can you do", "tell me about yourself", "who are you", "features"]
                }
            },
            "response_generator": {
                "responses": {
                    "greeting": [
                        "Hello! I'm a config-based bot.",
                        "Hi there! I was configured from a file.",
                        "Greetings! Nice to see you."
                    ],
                    "farewell": [
                        "Goodbye! Thanks for trying the config bot.",
                        "See you later! Have a great day.",
                        "Bye for now."
                    ],
                    "help": [
                        "I can demonstrate how configuration works in the E-CB framework.",
                        "I'm here to show you how to use ConfigLoader and ErrorHandler.",
                        "Need help? Try asking me about config files or error handling."
                    ],
                    "info": [
                        "I'm a chatbot configured from a JSON file. My responses, intents, and error handling are all defined in the configuration.",
                        "I demonstrate the E-CB framework's configuration system. My settings are loaded from a JSON file at startup."
                    ],
                    "unknown": [
                        "I'm not sure what you mean. My responses are defined in my configuration file.",
                        "I don't have a response for that in my configuration.",
                        "I don't know how to respond to that."
                    ]
                }
            }
        }
    }
    
    # Save to file based on extension
    file_extension = os.path.splitext(config_path)[1].lower()
    if file_extension == '.yaml' or file_extension == '.yml':
        with open(config_path, 'w') as f:
            yaml.dump(example_config, f, default_flow_style=False)
    else:  # Default to JSON
        with open(config_path, 'w') as f:
            json.dump(example_config, f, indent=2)
    
    print(f"Created example configuration at {config_path}")


def main():
    """Run a config-based chatbot."""
    # Determine config file path
    config_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'configs')
    config_path = os.path.join(config_dir, 'example_bot.json')
    
    # Create example config if needed
    create_example_config(config_path)
    
    # Initialize chatbot kernel with config
    kernel = ChatbotKernel(config_path)
    
    # Initialize components
    input_handler = InputHandler()
    
    # Choose NLU type based on config
    nlu_config = kernel.config.get('components', {}).get('nlu', {})
    nlu_type = nlu_config.get('type', 'simple')
    
    if nlu_type == 'spacy':
        nlu = SpacyNLU()
        # Configure custom intents if specified
        if 'custom_intents' in nlu_config:
            for intent_name, intent_data in nlu_config['custom_intents'].items():
                nlu.add_custom_intent(
                    intent_name,
                    keywords=intent_data.get('keywords', []),
                    patterns=intent_data.get('patterns', [])
                )
    else:
        nlu = SimpleNLU()
        # Configure intents if specified
        if 'intents' in nlu_config:
            nlu.patterns = nlu_config['intents']
    
    # Initialize response generator
    response_generator = ResponseGenerator()
    
    # Configure response templates if specified
    resp_config = kernel.config.get('components', {}).get('response_generator', {})
    if 'responses' in resp_config:
        response_generator.templates = resp_config['responses']
    
    # Register components
    kernel.register_component('input_handler', input_handler)
    kernel.register_component('nlu', nlu)
    kernel.register_component('response_generator', response_generator)
    
    # Optionally set up dialog manager
    if 'dialog_flows' in kernel.config:
        dialog_manager = DialogManager()
        
        # Register flows from config
        for flow_name, flow_def in kernel.config['dialog_flows'].items():
            dialog_manager.register_flow(flow_name, flow_def)
        
        # Register dialog manager
        kernel.register_component('dialog_manager', dialog_manager)
    
    # Start conversation
    bot_name = kernel.config.get('name', 'Config Bot')
    print(f"{bot_name} - {kernel.config.get('description', 'A config-based chatbot')}")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("You: ")
            
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print(f"Bot: {kernel.components['response_generator'].templates['farewell'][0]}")
                break
            
            response = kernel.process_message(user_input)
            print(f"Bot: {response}")
            
        except ChatbotError as e:
            # This should be handled by the kernel's error handler
            print(f"Bot: {str(e)}")
        
        except Exception as e:
            # Unexpected error
            print(f"System error: {e}")
            if kernel.config.get('debug', False):
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()