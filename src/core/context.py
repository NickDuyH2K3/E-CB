from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class ConversationContext:
    user_id: Optional[str] = None
    input_text: str = ""
    normalized_text: str = ""
    intent: Dict[str, Any] = field(default_factory=dict)
    entities: Dict[str, Any] = field(default_factory=dict)
    dialog_state: Dict[str, Any] = field(default_factory=dict)
    response: str = ""
    history: List[Dict[str, Any]] = field(default_factory=list)