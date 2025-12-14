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

        message = data.get("message", {})

        if message.get("type") != "tool.completed":
            return JSONResponse({"ignored": True})

        call = message.get("call", {})
        variables = call.get("variableValues", {})

        logger.info(f"Extracted variables: {variables}")

        user_name = variables.get("userName")
        meeting_date = variables.get("meetingDate")
        meeting_time = variables.get("meetingTime")
        meeting_title = variables.get("meetingTitle", "Meeting")

        if not user_name or not meeting_date or not meeting_time:
            logger.error("Missing required variables")
            return JSONResponse(
                {"success": False, "error": "Missing required fields"},
                status_code=400
            )

        event = calendar.create_event({
            "name": user_name,
            "date": meeting_date,
            "time": meeting_time,
            "title": meeting_title
        })

        logger.info("Calendar event created successfully")

        return JSONResponse(
            {"success": True, "message": "Event created", "event": event},
            status_code=200
        )

    except Exception as e:
        logger.exception("Webhook processing failed")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )
