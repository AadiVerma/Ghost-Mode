import json
import logging
from typing import List

from mediator.message.model import Message
from mediator.persona.model import Persona, PersonaStatus
from mediator.persona.time_filter import filter_by_age_range
from mediator.persona.voice_sampler import sample_voice
from ai.client import generate_json
from ai.prompts import PERSONA_EXTRACTOR_V1

logger = logging.getLogger(__name__)

class PersonaExtractor:
    @staticmethod
    async def extract(persona: Persona, all_messages: List[Message]) -> Persona:
        """
        Orchestrates the persona extraction process.
        """
        try:
            # 1. Filter by time
            filtered_msgs = filter_by_age_range(all_messages, persona.age_range)
            
            # 2. Sample representative messages
            sampled_msgs = sample_voice(filtered_msgs, sample_size=50)
            
            if not sampled_msgs:
                raise ValueError("No valid text messages found to extract persona.")

            # 3. Format messages for the prompt
            chat_log = ""
            for msg in sampled_msgs:
                chat_log += f"[{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {msg.sender}: {msg.content}\n"
            
            prompt = f"Here is the chat log:\n\n{chat_log}\n\nExtract the persona as requested in JSON format."

            # 4. Call LLM
            json_response_str = await generate_json(
                system_prompt=PERSONA_EXTRACTOR_V1,
                prompt=prompt
            )

            # 5. Parse JSON
            # Clean up the string in case Claude wraps it in ```json ... ```
            clean_json = json_response_str.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            clean_json = clean_json.strip()

            persona_data = json.loads(clean_json)

            # 6. Update Persona object
            persona.voice_signature = persona_data.get("voice_signature", {})
            persona.themes = persona_data.get("themes", [])
            persona.beliefs = persona_data.get("beliefs", [])
            persona.fears = persona_data.get("fears", [])
            persona.relationships = persona_data.get("relationships", {})
            persona.sample_messages = persona_data.get("sample_messages", [])
            
            persona.status = PersonaStatus.READY
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Failed to extract persona: {str(e)}")
            persona.status = PersonaStatus.FAILED
            
        return persona
