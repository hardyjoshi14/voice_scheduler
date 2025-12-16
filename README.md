

# 🗣️ Voice Scheduling AI Agent

A real-time voice assistant that schedules meetings via natural conversation. Users provide details, the agent confirms them, and a real event is created on Google Calendar.

## 🚀 Live Deployment

*   **Voice Agent**: Accessible via VAPI dashboard *(https://dashboard.vapi.ai/assistants/878340b4-0042-4fd9-937f-4a97b7107303)* 
Demo link * (https://vapi.ai?demo=true&shareKey=5c6fda75-49aa-4f71-b74f-f1f31b167d2e&assistantId=878340b4-0042-4fd9-937f-4a97b7107303)*
*   **Backend API**: `https://voice-scheduler-ten.vercel.app`

## 📞 How to Test

1.  Initiate a call to the agent.
2.  Follow the conversation: provide your **name**, **date** **time** , and a **meeting title**.
3.  Confirm the details. The agent will say "Your meeting has been scheduled successfully."
4.  Check the connected Google Calendar for the new event titled "*{Title} with {Name}*".

## 🛠️ Technical Overview

**Voice Layer (VAPI.ai)**:
-   **LLM**: GPT-4o for natural dialogue.
-   **Voice**: Azure `en-US-JennyNeural`.
-   **System Prompt**: Guides the agent to collect `userName`, `meetingDate`, `meetingTime`, and `meetingTitle`, confirm, then call the `schedule_meeting` function.

**Backend (FastAPI on Vercel)**:
-   **Framework**: FastAPI, deployed on Vercel.
-   **Key Endpoint**: `POST /webhook` – processes VAPI's `tool-calls`, validates data, and interfaces with Google Calendar.

**Calendar Integration**:
-   **Technology**: Google Calendar API v3.
-   **Authentication**: Secure Service Account. The JSON key is stored as a `SERVICE_ACCOUNT_JSON` environment variable in Vercel.
-   **Process**: Authenticates, formats date/time, and creates a 1-hour event on the primary calendar.

## 💻 Local Setup

1.  **Clone & Install**:
    ```bash
    git clone https://github.com/hardyjoshi14/voice-scheduler.git
    cd voice-scheduler
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    Create a `.env` file: `SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'`

3.  **Run Server**:
    ```bash
    cd api
    uvicorn index:app --reload
    # Server runs at http://localhost:8000
    ```

4.  **Test & Connect Agent**:
    - Test the API: `curl http://localhost:8000/debug`
    - Use **ngrok** (`ngrok http 8000`) to get a public URL.
    - In VAPI dashboard, set your agent's **Server URL** to your ngrok URL (e.g., `https://abcd.ngrok.app/webhook`).

## Evidence

Check the `/agent_logs` folder for tool calls and transcript

**Sample API Response**:
```json
{
  "results": [{
    "toolCallId": "call_abc123",
    "result": "Meeting scheduled for Hardy Joshi on 2024-12-16 at 13:00. Title: Meeeting. Event ID: event-123"
  }]
}
```
Note - Currently only meeting id is returned. The webhook can be configured to return meeting link as well to check the event on calendar.

## 🔧 Troubleshooting

-   **"No result returned" in VAPI**: Ensure your `/webhook` returns the exact JSON format shown above.
-   **Calendar Service not available**: Verify the `SERVICE_ACCOUNT_JSON` environment variable is correctly set in Vercel.
