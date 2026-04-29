import re
from datetime import datetime
from typing import Generator
from dateutil.parser import parse as parse_date

from .base import BaseParser, ParsedMessage

class WhatsAppParser(BaseParser):
    def parse(self, file_path: str) -> Generator[ParsedMessage, None, None]:
        # Regex to match WhatsApp log lines
        # Works for: [24/05/23, 10:15:23 AM] John Doe: Hey
        # Works for: 12/04/2023, 15:30 - Jane: I'm good!
        pattern = re.compile(
            r'^\[?(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),?\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?(?:\s?[aApP][mM])?)\]?[ \-]*(?P<sender>[^:]+):\s*(?P<content>.*)$'
        )

        current_message = None

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                match = pattern.match(line)
                if match:
                    if current_message:
                        yield current_message
                    
                    date_str = match.group("date")
                    time_str = match.group("time")
                    sender = match.group("sender").strip()
                    content = match.group("content").strip()

                    try:
                        dt_str = f"{date_str} {time_str}"
                        # Allow dayfirst as typical in many WhatsApp locales.
                        # It will fallback if impossible.
                        timestamp = parse_date(dt_str, dayfirst=True)
                    except Exception:
                        timestamp = datetime.now()

                    content_lower = content.lower()
                    is_media = (
                        "omitted" in content_lower 
                        or "<media omitted>" in content_lower
                    )

                    current_message = ParsedMessage(
                        timestamp=timestamp,
                        sender=sender,
                        content=content,
                        is_media=is_media
                    )
                else:
                    if current_message:
                        current_message.content += f"\n{line}"
        
        if current_message:
            yield current_message
