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
    """
    Webhook for VAPI calls
    {
        "call": {
            "variables": {
                "userName": "Alice",
                "meetingDate": "2025-12-15",
                "meetingTime": "14:30",
                "meetingTitle": "Project Sync"
            }
        }
    }
    """
    try:
        data = await request.json()
        logger.info(f"Webhook received: {data}")

        vars = data.get("call", {}).get("variables", {})
        if not vars.get("userName") or not vars.get("meetingDate") or not vars.get("meetingTime"):
            return JSONResponse({"success":False, "error": "Missing required fields"})
        
        event = calendar.create_event({
            "name": vars["userName"],
            "date": vars["meetingDate"],
            "time": vars["meetingTime"],
            "title": vars.get("meetingTitle", "Meeting")
        })
        return JSONResponse({"success": True, "message": "Event created", "event": event})
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
    
    