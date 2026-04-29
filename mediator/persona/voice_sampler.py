import random
from typing import List
from mediator.message.model import Message

def sample_voice(messages: List[Message], sample_size: int = 50) -> List[Message]:
    """
    Selects a representative sample of messages for the LLM prompt.
    For MVP, we randomly sample to get a mix of short, long, and varied contexts,
    filtering out media messages.
    """
    text_messages = [m for m in messages if not m.is_media and m.content.strip()]
    
    if len(text_messages) <= sample_size:
        return text_messages
        
    # Random sample is decent, but could be improved later (e.g. longest, most emotional)
    return random.sample(text_messages, sample_size)
