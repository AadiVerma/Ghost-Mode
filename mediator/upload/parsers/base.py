import abc
from dataclasses import dataclass
from datetime import datetime
from typing import Generator

@dataclass
class ParsedMessage:
    timestamp: datetime
    sender: str
    content: str
    is_media: bool

class BaseParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, file_path: str) -> Generator[ParsedMessage, None, None]:
        """Parse a chat export file and yield ParsedMessage objects."""
        pass
