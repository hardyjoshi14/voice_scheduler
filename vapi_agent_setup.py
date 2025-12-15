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

with open("system_prompt.txt", "r") as f:
    system_prompt = f.read()

agent_config = {
    "name": "Voice Scheduler",
    "firstMessage": "Hello! I'm your scheduling assistant. May I have your name?",
    "endCallMessage": "Your meeting has been scheduled successfully. Goodbye.",
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
                "content": system_prompt
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "schedule_meeting",
                    "description": "Schedule a meeting when all details are collected and confirmed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "userName": {
                                "type": "string",
                                "description": "Full name of the user"
                            },
                            "meetingDate": {
                                "type": "string", 
                                "description": "Date in YYYY-MM-DD format (e.g., 2024-12-15)"
                            },
                            "meetingTime": {
                                "type": "string",
                                "description": "Time in HH:MM format (24-hour, e.g., 14:30)"
                            },
                            "meetingTitle": {
                                "type": "string",
                                "description": "Title/description of the meeting"
                            }
                        },
                        "required": ["userName", "meetingDate", "meetingTime", "meetingTitle"]
                    }
                }
            }
        ]
    },
    "voice": {
        "provider": "azure", 
        "voiceId": "en-US-JennyNeural"
    },
    "transcriber": {
        "provider": "deepgram", 
        "model": "nova-2"
    },
    "server": {
        "url": WEBHOOK_URL, 
        "timeoutSeconds": 20
    }
}

response = requests.post(
    "https://api.vapi.ai/assistant",
    headers=headers,
    json=agent_config
)

if response.status_code == 201:
    agent = response.json()
    print("✅ Agent created successfully!")
    print(f"Agent ID: {agent['id']}")
    print(f"Dashboard URL: https://dashboard.vapi.ai/assistants/{agent['id']}")
else:
    print(f"Failed to create agent: {response.status_code}")
    print(f"Response: {response.text}")