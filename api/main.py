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
        payload = await request.json()
        logger.info(f"Webhook received: {payload}")

        message = payload.get("message", {})
        call = message.get("call", {})
        vars = call.get("variableValues", {})

        if message.get("type") != "conversation-update":
            return JSONResponse({"ok": True})

        user_name = vars.get("userName")
        meeting_date = vars.get("meetingDate")
        meeting_time = vars.get("meetingTime")
        meeting_title = vars.get("meetingTitle", "Meeting")

        if not user_name or not meeting_date or not meeting_time:
            logger.info("Variables not complete yet, skipping")
            return JSONResponse({"ok": True})

        event = calendar.create_event({
            "name": user_name,
            "date": meeting_date,
            "time": meeting_time,
            "title": meeting_title
        })

        logger.info("Calendar event created successfully")

        return JSONResponse({
            "success": True,
            "event": event
        })

    except Exception as e:
        logger.exception("Webhook error")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )
