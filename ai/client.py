import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    has_key = True
else:
    has_key = False

async def generate_json(system_prompt: str, prompt: str) -> str:
    """
    Calls Google Gemini to generate a JSON response.
    """
    if not has_key:
        logger.warning("No GEMINI_API_KEY found. Returning MOCK persona data.")
        mock_response = {
            "voice_signature": {
                "tone": "angsty and sarcastic",
                "recurring_phrases": ["literally", "im dead", "fr fr"],
                "punctuation_style": "all lowercase, no periods",
                "emoji_habits": "excessive skull emojis 💀"
            },
            "themes": ["school stress", "crushes", "video games"],
            "beliefs": ["nobody understands me", "math is useless"],
            "fears": ["failing exams", "being left out"],
            "relationships": {
                "John Doe": "best friend, complains about him often"
            },
            "sample_messages": [
                "i literally cant do this right now",
                "bro im so dead 💀",
                "math is actually the worst thing ever invented"
            ]
        }
        return json.dumps(mock_response)

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7
        )
    )
    response = await model.generate_content_async(prompt)
    return response.text

async def generate_chat_response(system_prompt: str, chat_history: list) -> str:
    """
    Calls Google Gemini to generate the next chat message.
    chat_history should be a list of dicts: [{"role": "user"|"assistant", "content": "..."}]
    """
    if not has_key:
        logger.warning("No GEMINI_API_KEY found. Returning MOCK chat response.")
        return "literally why are you talking to me rn 💀"

    formatted_history = []
    for msg in chat_history:
        role = "model" if msg["role"] == "assistant" else "user"
        formatted_history.append({"role": role, "parts": [msg["content"]]})

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.8
        )
    )
    
    response = await model.generate_content_async(formatted_history)
    return response.text
