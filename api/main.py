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

        # ✅ 1. Ignore ALL non-final events
        if message_type != "tool.completed":
            return JSONResponse({"success": True})

        # ✅ 2. ONLY handle final tool call
        variables = data.get("call", {}).get("variableValues", {})

        required = ["userName", "meetingDate", "meetingTime"]
        if not all(variables.get(k) for k in required):
            logger.warning("Missing required variables on tool.completed")
            return JSONResponse({"success": False, "error": "Missing required fields"})

        event = calendar.create_event({
            "name": variables["userName"],
            "date": variables["meetingDate"],
            "time": variables["meetingTime"],
            "title": variables.get("meetingTitle", "Meeting")
        })

        return JSONResponse({
            "success": True,
            "message": "Event created",
            "event": event
        })

    except Exception as e:
        logger.exception("Webhook error")
        return JSONResponse({"success": False, "error": str(e)}, status_code=200)
