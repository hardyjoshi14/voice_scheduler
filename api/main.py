# webhook_server.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from calendar_scheduler import CalendarService  # your service to save events

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
        call = data.get("call", {})

        variables = call.get("variableValues", {})

        if variables.get("userName") and variables.get("meetingDate") and variables.get("meetingTime") and variables.get("meetingTitle"):

            event = calendar.create_event({
                "name": variables["userName"],
                "date": variables["meetingDate"],
                "time": variables["meetingTime"],
                "title": variables.get("meetingTitle", "Meeting")
            })
            logger.info(f"Meeting created: {event}")

        return JSONResponse({"ok": True})

    except Exception as e:
        logger.exception("Webhook failed")
        return JSONResponse({"ok": True})
