import sys
import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

project_root = os.path.dirname(os.path.dirname(__file__))  
sys.path.insert(0, project_root)  
sys.path.append(project_root)    

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"✅ Current directory: {os.getcwd()}")
logger.info(f"✅ Project root added to path: {project_root}")
if os.path.exists(project_root):
    logger.info(f"✅ Files in project root: {os.listdir(project_root)}")

app = FastAPI(title="Voice Scheduler API")

try:
    from calendar_scheduler import CalendarService
    calendar = CalendarService()
    logger.info("CalendarService imported successfully")
except ImportError as e:
    logger.error(f"Failed to import CalendarService: {e}")
    logger.error(f"Python path is: {sys.path}")
    calendar = None
except Exception as e:
    logger.error(f"CalendarService initialization failed: {e}")
    calendar = None

@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": "Voice Scheduler API", 
        "status": "ok", 
        "framework": "FastAPI",
        "calendar_service": "available" if calendar else "unavailable"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "framework": "FastAPI"}

@app.post("/webhook")
async def webhook(request: Request):
    """
    Main webhook endpoint for VAPI function calls
    Expected payload from VAPI:
    {
        "message": {
            "type": "function-call",
            "functionCall": {
                "name": "schedule_meeting",
                "toolCallId": "abc123",
                "arguments": {
                    "userName": "John Doe",
                    "meetingDate": "2024-12-15",
                    "meetingTime": "14:30",
                    "meetingTitle": "Project Kickoff"
                }
            }
        }
    }
    """
    try:
        data = await request.json()
        logger.info(f"Webhook received: {data.get('message', {}).get('type')}")
        
        message = data.get("message", {})
        message_type = message.get("type")
        
        if message_type == "function-call":
            function_call = message.get("functionCall", {})
            function_name = function_call.get("name")
            tool_call_id = function_call.get("toolCallId")
            
            logger.info(f"Function call: {function_name}, ID: {tool_call_id}")
            
            if function_name == "schedule_meeting":
                arguments = function_call.get("arguments", {})
                
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse arguments: {e}")
                        return JSONResponse({
                            "results": [{
                                "toolCallId": tool_call_id,
                                "result": f"Error parsing arguments: {str(e)}"
                            }]
                        })
                
                logger.info(f"Meeting details: {arguments}")
                
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
                    logger.error("CalendarService not available")
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
                    logger.error(f"Failed to create calendar event: {str(e)}")
                    return JSONResponse({
                        "results": [{
                            "toolCallId": tool_call_id,
                            "result": f"Error creating calendar event: {str(e)}"
                        }]
                    })
        
        elif message_type in ["assistant.started", "status-update", "speech-update", "transcript", "conversation-update"]:
            logger.info(f"Acknowledging message type: {message_type}")
            return JSONResponse({"ok": True})
        
        return JSONResponse({"ok": True})
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        return JSONResponse({"ok": True})

@app.post("/test-schedule")
async def test_schedule():
    """
    Test endpoint to verify calendar integration works
    Use this to test without VAPI
    """
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
        logger.error(f"Test schedule failed: {str(e)}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)