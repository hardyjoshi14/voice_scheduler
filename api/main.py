from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from calendar_scheduler import CalendarService  
import json
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

try:
    calendar = CalendarService()
    logger.info("✅ CalendarService initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize CalendarService: {e}")
    calendar = None

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"📥 Webhook received, message type: {data.get('message', {}).get('type')}")
        
        message = data.get("message", {})
        message_type = message.get("type")
        
        logger.debug(f"Full webhook data:\n{json.dumps(data, indent=2)}")
        
        if message_type == "function-call":
            function_call = message.get("functionCall", {})
            function_name = function_call.get("name")
            tool_call_id = function_call.get("toolCallId")
            
            logger.info(f"🔧 Function call received: {function_name}, toolCallId: {tool_call_id}")
            
            if function_name == "schedule_meeting":
                arguments = function_call.get("arguments", {})
                
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                        logger.info(f"Parsed arguments: {arguments}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse arguments: {arguments}, error: {e}")
                        return JSONResponse({
                            "results": [{
                                "toolCallId": tool_call_id,
                                "result": f"Error parsing arguments: {str(e)}"
                            }]
                        })
                
                logger.info(f"📋 Meeting details: {arguments}")
                
                required_fields = ["userName", "meetingDate", "meetingTime", "meetingTitle"]
                missing_fields = [field for field in required_fields if field not in arguments]
                
                if missing_fields:
                    logger.error(f"Missing fields: {missing_fields}")
                    return JSONResponse({
                        "results": [{
                            "toolCallId": tool_call_id,
                            "result": f"Missing required fields: {missing_fields}"
                        }]
                    })
                
                if calendar is None:
                    logger.error("CalendarService not initialized")
                    return JSONResponse({
                        "results": [{
                            "toolCallId": tool_call_id,
                            "result": "Calendar service not available"
                        }]
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
                        "results": [{
                            "toolCallId": tool_call_id,
                            "result": {
                                "success": True,
                                "message": "Meeting scheduled successfully",
                                "event_id": event.get("id"),
                                "event_link": event.get("link"),
                                "summary": event.get("summary")
                            }
                        }]
                    })
                    
                except Exception as e:
                    error_msg = f"Failed to create calendar event: {str(e)}"
                    logger.error(f"{error_msg}\n{traceback.format_exc()}")
                    
                    return JSONResponse({
                        "results": [{
                            "toolCallId": tool_call_id,
                            "result": error_msg
                        }]
                    })
        
        elif message_type in [
            "assistant.started", 
            "status-update", 
            "speech-update", 
            "transcript", 
            "conversation-update",
            "user-interrupted",
            "hang"
        ]:
            logger.info(f"📨 Acknowledging message type: {message_type}")
            return JSONResponse({"ok": True})
        
        logger.info(f"Unknown message type: {message_type}")
        return JSONResponse({"ok": True})
        
    except Exception as e:
        logger.exception(f"Webhook processing failed: {e}")
        return JSONResponse({"ok": True})

@app.get("/test")
async def test():
    return {
        "status": "running",
        "endpoints": {
            "webhook": "POST /webhook",
            "health": "GET /health",
            "test-schedule": "POST /test-schedule"
        }
    }

@app.post("/test-schedule")
async def test_schedule():
    """Test endpoint to verify calendar integration works"""
    if calendar is None:
        return JSONResponse({
            "success": False,
            "error": "Calendar service not initialized"
        }, status_code=500)
    
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
        logger.exception(f"Test schedule failed: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status_code=500)

@app.get("/")
async def root():
    return {
        "message": "Voice Scheduler Webhook",
        "status": "online",
        "endpoints": ["/webhook", "/health", "/test", "/test-schedule"]
    }