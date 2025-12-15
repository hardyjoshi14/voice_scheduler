from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from calendar_scheduler import CalendarService  
import json

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
        logger.info(f"Webhook received, message type: {data.get('message', {}).get('type')}")
        
        message = data.get("message", {})
        message_type = message.get("type")
        
        logger.debug(f"Full data: {json.dumps(data, indent=2)[:1000]}")
        
        if message_type == "function-call":
            function_call = message.get("functionCall", {})
            function_name = function_call.get("name")
            
            logger.info(f"Function call received: {function_name}")
            
            if function_name == "schedule_meeting":
                arguments = function_call.get("arguments", {})
                
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse arguments: {arguments}")
                        return JSONResponse({
                            "result": "Error parsing arguments"
                        })
                
                logger.info(f"Meeting details: {arguments}")
                
                required_fields = ["userName", "meetingDate", "meetingTime", "meetingTitle"]
                missing_fields = [field for field in required_fields if field not in arguments]
                
                if missing_fields:
                    logger.error(f"Missing fields: {missing_fields}")
                    return JSONResponse({
                        "result": f"Missing required fields: {missing_fields}"
                    })
                
                try:
                    event = calendar.create_event({
                        "name": arguments["userName"],
                        "date": arguments["meetingDate"],
                        "time": arguments["meetingTime"],
                        "title": arguments["meetingTitle"]
                    })
                    
                    logger.info(f"Calendar event created: {event}")
                    
                    return JSONResponse({
                        "result": {
                            "success": True,
                            "message": "Meeting scheduled successfully",
                            "event_id": event.get("id"),
                            "event_link": event.get("link")
                        }
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to create calendar event: {e}")
                    return JSONResponse({
                        "result": f"Error creating calendar event: {str(e)}"
                    })
        
        elif message_type in ["assistant.started", "status-update", "speech-update", "transcript", "conversation-update"]:
            return JSONResponse({"ok": True})
    
        return JSONResponse({"ok": True})
        
    except Exception as e:
        logger.exception(f"Webhook processing failed: {e}")
        return JSONResponse({"ok": True})

@app.post("/test-schedule")
async def test_schedule():
    """Test endpoint to verify calendar integration works"""
    try:
        test_data = {
            "name": "Test User",
            "date": "2024-12-15",
            "time": "14:30",
            "title": "Test Meeting"
        }
        
        event = calendar.create_event(test_data)
        
        return JSONResponse({
            "success": True,
            "message": "Test event created successfully",
            "event": event
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)