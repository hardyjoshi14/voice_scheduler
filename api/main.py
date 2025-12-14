from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .calendar_scheduler import CalendarService
import logging

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
        logger.info(f"Webhook received: {data}")

        message_type = data.get("message", {}).get("type")
        call = data.get("call", {})
        variables = call.get("variableValues") or call.get("variables") or {}

        # ✅ Always ACK non-final events
        if message_type != "conversation-update":
            return JSONResponse({"success": True})

        # ✅ Only proceed when all required variables exist
        required_fields = ["userName", "meetingDate", "meetingTime"]
        if not all(variables.get(f) for f in required_fields):
            logger.info("Conversation update received, but variables incomplete.")
            return JSONResponse({"success": True})

        # ✅ Create calendar event ONCE
        event = calendar.create_event({
            "name": variables["userName"],
            "date": variables["meetingDate"],
            "time": variables["meetingTime"],
            "title": variables.get("meetingTitle", "Meeting")
        })

        logger.info("Calendar event created successfully")

        return JSONResponse({
            "success": True,
            "message": "Event created",
            "event": event
        })

    except Exception as e:
        logger.exception("Webhook processing failed")
        # ⚠️ Still return 200 so Vapi doesn't break the call
        return JSONResponse({"success": False, "error": str(e)})
