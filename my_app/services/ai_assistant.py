from typing import List, Dict
from google import genai
from google.genai import types

class AIAssistant:
    """Simple wrap around of Gemini API"""
    # Initializes the objects
    def __init__(self, api_key: str, system_prompt: str = "You are a helpful assistant."):
        self._system_prompt = system_prompt
        self._history: List[Dict[str, str]] = []
        self._client = genai.Client(api_key=api_key)

    # Set system prompt
    def set_system_prompt(self, prompt: str):
        """Sets the system prompt."""
        self._system_prompt = prompt

    # Send massage
    def send_message(self, user_message: str, category: str = "General", data_text: str = "") -> str:
        """Send a message to Gemini and stream back the response."""
        # Add user message to history
        self._history.append({"role": "user", "parts": [{"text": user_message}]})

        # Build contents
        contents = [
            *self._history,
            {"role": "user", "parts": [{"text": f"Here is the {category} table:\n{data_text}"}]}
        ]
        # API config
        response_stream = self._client.models.generate_content_stream(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=f"You are an {category} data analyst. Your name is Gem."
            ),
            contents=contents
        )

        # Collect streaming response
        full_reply = ""
        for chunk in response_stream:
            full_reply += chunk.text

        # Save assistant reply
        self._history.append({"role": "assistant", "parts": [{"text": full_reply}]})
        return full_reply

    # Clear history
    def clear_history(self):
        """Clears the history of the API assistant."""
        self._history.clear()

    # Get history
    def get_history(self) -> List[Dict[str, str]]:
        """Returns the history of the API assistant."""
        return self._history