from typing import List
from mediator.message.model import Message

def filter_by_age_range(messages: List[Message], age_range: str) -> List[Message]:
    """
    Filters messages by the requested age range.
    For MVP, since we don't know the user's exact birthdate to map '17-19' to absolute dates,
    we will assume age_range is just a label for now and use all messages, 
    or we can parse specific years if the user passes '2015-2017' instead.
    
    If age_range is 'all', return all messages.
    """
    if age_range.lower() == "all":
        return messages
        
    # TODO: Implement proper birthdate to date-range mapping when User profile has DOB
    return messages
