import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

agent_config = {
    "name": "Voice Scheduler",
    "firstMessage": "Hello! I'm your scheduling assistant. May I have your name?",
    "silenceTimeoutSeconds": 15,
    "maxDurationSeconds": 300,
    "model": {
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.5,
        "maxTokens": 250,
        "messages": [
            {
                "role": "system",
                "content": open("system_prompt.txt").read()
            }
        ]
    },
    "voice": {"provider": "azure", "voiceId": "en-US-JennyNeural"},
    "transcriber": {"provider": "deepgram", "model": "nova-2"},
    "server": {"url": WEBHOOK_URL, "timeoutSeconds": 20},
    "clientMessages": ["tool-calls","tool-calls-result","status-update"],
}


response = requests.post(
    "https://api.vapi.ai/assistant",
    headers=headers,
    json=agent_config
)
if response.status_code == 201:
    agent = response.json()
    print("Agent created successfully!")
    print(f"Agent ID: {agent['id']}")
    print(f"Dashboard URL: https://dashboard.vapi.ai/assistants/{agent['id']}")
else:
    print(f"Failed to create agent: {response.status_code} - {response.text}")

