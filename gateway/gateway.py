import requests
import json
from typing import List, Dict

def chat_with_model(messages: List[Dict[str, str]], persona: str = "default") -> str:
    """
    Send a list of messages (conversation history) to the model API and return the reply.
    Each message should be a dict with keys: {"role": "system"|"user"|"assistant", "content": str}
    """
    try:
        # Load app config
        with open("config/app.json") as f:
            cfg = json.load(f)

        # Load persona config
        with open("config/persona.json") as f:
            personas = json.load(f)
        system_prompt = personas.get(persona, personas["default"])

        # Ensure system prompt is always first
        if messages[0]["role"] != "system":
            messages = [system_prompt] + messages
        else:
            messages[0] = system_prompt

        response = requests.post(
            cfg["endpoint"],
            json={
                "model": cfg["model"],
                "messages": messages,
                "max_tokens": cfg["max_tokens"]
            },
            timeout=10
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error talking to model: {e}"