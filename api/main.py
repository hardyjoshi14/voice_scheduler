from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from calendar_scheduler import CalendarService  
import json
from datetime import datetime

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
        logger.info(f"Received webhook data: {json.dumps(data, indent=2)[:500]}...")
        
        message = data.get("message", {})
        message_type = message.get("type")
        
        logger.info(f"Message type: {message_type}")
        
        if message_type in ["assistant.started", "status-update", "speech-update", "transcript"]:
            return JSONResponse({"ok": True})
        
        elif message_type == "conversation-update":
            call = data.get("call", {})
            variables = call.get("variableValues", {})
            
            logger.info(f"Variables received: {variables}")
            
            required = ["userName", "meetingDate", "meetingTime"]
            if all(variables.get(k) for k in required):
                logger.info("All required variables found, creating calendar event...")
                
                event = calendar.create_event({
                    "name": variables["userName"],
                    "date": variables["meetingDate"],
                    "time": variables["meetingTime"],
                    "title": variables.get("meetingTitle", "Meeting")
                })
                
                logger.info(f"Meeting created successfully: {event}")
                
                return JSONResponse({
                    "ok": True,
                    "event_created": True,
                    "event": event
                })
        return JSONResponse({"ok": True})
        
    except Exception as e:
        logger.exception(f"Webhook failed: {e}")
        return JSONResponse({"ok": True})

@app.post("/test-webhook")
async def test_webhook(request: Request):
    """Test endpoint to simulate VAPI webhook call"""
    test_data = {
        "message": {
            "type": "conversation-update",
            "timestamp": 1234567890
        },
        "call": {
            "variableValues": {
                "userName": "John Doe",
                "meetingDate": "2024-12-15",
                "meetingTime": "14:30",
                "meetingTitle": "Test Meeting"
            }
        }
    }
    
    try:
        event = calendar.create_event({
            "name": test_data["call"]["variableValues"]["userName"],
            "date": test_data["call"]["variableValues"]["meetingDate"],
            "time": test_data["call"]["variableValues"]["meetingTime"],
            "title": test_data["call"]["variableValues"]["meetingTitle"]
        })
        
        return JSONResponse({
            "success": True,
            "message": "Test event created",
            "event": event
        })
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        }, status_code=500)