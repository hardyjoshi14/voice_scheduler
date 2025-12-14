from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

from calendar_scheduler import CalendarService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
calendar = CalendarService()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()

        message = data.get("message", {})
        message_type = message.get("type")

        call = data.get("call", {})
        variables = call.get("variableValues") or {}

        if message_type != "conversation-update":
            return JSONResponse({"ok": True})

        required = ["userName", "meetingDate", "meetingTime"]
        if not all(variables.get(k) for k in required):
            return JSONResponse({"ok": True})

        event = calendar.create_event({
            "name": variables["userName"],
            "date": variables["meetingDate"],
            "time": variables["meetingTime"],
            "title": variables.get("meetingTitle", "Meeting")
        })

        return JSONResponse({
            "success": True,
            "event": event
        })

    except Exception as e:
        logger.exception("Webhook failed")
        return JSONResponse({"ok": True})
