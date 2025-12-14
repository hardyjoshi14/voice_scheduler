import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Your webhook to save meetings

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Step 1: Create the saveMeeting tool
tool_config = {
    "name": "saveMeeting",
    "description": "Save the confirmed meeting info to the webhook",
    "type": "webhook",
    "server": {"url": WEBHOOK_URL, "timeoutSeconds": 20},
    "inputParameters": [
        {"name": "userName", "type": "string", "required": True},
        {"name": "meetingDate", "type": "string", "required": True},
        {"name": "meetingTime", "type": "string", "required": True},
        {"name": "meetingTitle", "type": "string", "required": True},
    ]
}

tool_resp = requests.post(
    "https://api.vapi.ai/tool",
    headers=HEADERS,
    json=tool_config
)

if tool_resp.status_code == 201:
    tool_id = tool_resp.json()["id"]
    print(f"Tool created successfully! ID: {tool_id}")
else:
    print(f"Failed to create tool: {tool_resp.status_code} - {tool_resp.text}")
    exit(1)

# Step 2: Create the Voice Scheduler agent
with open("system_prompt.txt") as f:
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
            {"role": "system", "content": system_prompt}
        ]
    },
    "voice": {"provider": "azure", "voiceId": "en-US-JennyNeural"},
    "transcriber": {"provider": "deepgram", "model": "nova-2"},
    "server": {"url": WEBHOOK_URL, "timeoutSeconds": 20},
    "tools": [tool_id],
    "clientMessages": ["tool-calls","tool-calls-result","status-update"],
}

agent_resp = requests.post(
    "https://api.vapi.ai/assistant",
    headers=HEADERS,
    json=agent_config
)

if agent_resp.status_code == 201:
    agent = agent_resp.json()
    print("Agent created successfully!")
    print(f"Agent ID: {agent['id']}")
    print(f"Dashboard URL: https://dashboard.vapi.ai/assistants/{agent['id']}")
else:
    print(f"Failed to create agent: {agent_resp.status_code} - {agent_resp.text}")
