import spacy
from typing import Dict, Any, List
import difflib

class SpacyNLU:
    """
    Enhanced Natural Language Understanding component
    with advanced intent recognition and entity extraction.
    """
    
    def __init__(self, model='en_core_web_sm'):
        """
        Initialize the NLU with a spaCy language model.
        
        Args:
            model: spaCy language model to use
        """
        try:
            self.nlp = spacy.load(model)
        except OSError:
            print(f"Downloading language model {model}")
            spacy.cli.download(model)
            self.nlp = spacy.load(model)
        
        # More sophisticated intent patterns
        self.intent_patterns = {
            'greeting': {
                'keywords': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon'],
                'patterns': [
                    'hi there', 
                    'how are you', 
                    'nice to meet you'
                ]
            },
            'help_request': {
                'keywords': ['help', 'support', 'assist', 'problem', 'issue', 'can you help'],
                'patterns': [
                    'i need help with', 
                    'can you assist me', 
                    'i have a question'
                ]
            },
            'farewell': {
                'keywords': ['bye', 'goodbye', 'see you', 'farewell', 'talk later'],
                'patterns': [
                    'i am leaving', 
                    'got to go', 
                    'catch you later'
                ]
            },
            'thanks': {
                'keywords': ['thank', 'appreciate', 'thanks', 'thank you'],
                'patterns': [
                    'that was helpful', 
                    'thanks a lot', 
                    'much appreciated'
                ]
            }
        }
    
    def _fuzzy_match(self, text: str, patterns: List[str], threshold: float = 0.6) -> bool:
        """
        Perform fuzzy matching of text against patterns.
        
        Args:
            text: Input text to match
            patterns: List of pattern strings
            threshold: Similarity threshold
        
        Returns:
            Boolean indicating if a match is found
        """
        return any(
            difflib.SequenceMatcher(None, text.lower(), pattern.lower()).ratio() >= threshold
            for pattern in patterns
        )
    
    def get_intent(self, text: str) -> Dict[str, Any]:
        """
        Extract intent with more context and details.
        
        Args:
            text: User input text
            
        Returns:
            Dictionary with intent details
        """
        # Process the text with spaCy
        doc = self.nlp(text.lower())
        
        # Extract entities
        entities = self._extract_entities(doc)
        
        # Check for intent based on advanced matching
        for intent, pattern_data in self.intent_patterns.items():
            # Check keywords
            keyword_match = any(
                keyword in text.lower() 
                for keyword in pattern_data.get('keywords', [])
            )
            
            # Check pattern matching
            pattern_match = self._fuzzy_match(
                text, 
                pattern_data.get('patterns', [])
            )
            
            # Calculate confidence
            if keyword_match or pattern_match:
                confidence = 0.8 if keyword_match else 0.6
                return {
                    'name': intent,
                    'confidence': confidence,
                    'entities': entities
                }
        
        # Fallback intent
        return {
            'name': 'unknown',
            'confidence': 0.2,
            'entities': entities
        }
    
    def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """
        Extract named entities from the processed document.
        
        Args:
            doc: spaCy processed document
        
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        
        # Custom entity extraction
        # Add more custom entity types as needed
        entities['keywords'] = [
            token.text for token in doc 
            if token.pos_ in ['NOUN', 'VERB']
        ]
        
        return entities
    
    def add_custom_intent(self, name: str, keywords: List[str], patterns: List[str] = None):
        """
        Allow dynamic addition of intent patterns.
        
        Args:
            name: Name of the intent
            keywords: List of keywords for the intent
            patterns: Optional list of pattern strings
        """
        self.intent_patterns[name] = {
            'keywords': keywords,
            'patterns': patterns or []
        }