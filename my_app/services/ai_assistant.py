from typing import List, Dict
from google import genai
from google.genai import types

class AIAssistant:
    """Simple wrap around of Gemini API"""
    def __init__(self, api_key: str, system_prompt: str = "You are a helpful assistant."):
        self._system_prompt = system_prompt
        self._history: List[Dict[str, str]] = []
        self._client = genai.Client(api_key=api_key)

    def set_system_prompt(self, prompt: str):
        self._system_prompt = prompt

    def send_message(self, user_message: str, category: str = "General", data_text: str = "") -> str:
        """Send a message to Gemini and stream back the response."""
        # Add user message to history
        self._history.append({"role": "user", "parts": [{"text": user_message}]})

        # Build contents
        contents = [
            *self._history,
            {"role": "user", "parts": [{"text": f"Here is the {category} table:\n{data_text}"}]}
        ]

        response_stream = self._client.models.generate_content_stream(
            model="gemini-3-pro-preview",
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

    def clear_history(self):
        self._history.clear()

    def get_history(self) -> List[Dict[str, str]]:
        return self._history




# from typing import List, Dict
#
# class AIAssistant:
#     """Simple wrapper around an AI/chat model.
#     In your real project, connect this to OpenAI or another provider.
#     """
#     def __init__(self, system_prompt: str = "You are a helpful assistant."):
#         self._system_prompt = system_prompt
#         self._history: List[Dict[str, str]] = []
#
#     def set_system_prompt(self, prompt: str) :
#         self._system_prompt = prompt
#
#     def send_message(self, user_message: str) :
#         """Send a message and get a (fake) response.
#         Replace this body with your real API call.
#         """
#         self._history.append({"role": "user", "content": user_message})
#         # Fake response for now:
#         response = f"[AI reply to]: {user_message[:50]}"
#         self._history.append({"role": "assistant", "content": response})
#         return response
#
#     def clear_history(self):
#         self._history.clear()