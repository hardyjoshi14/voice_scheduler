import sys
import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.dirname(__file__))  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"✅ Current directory: {os.getcwd()}")
logger.info(f"✅ Files in current dir: {os.listdir('.')}")

app = FastAPI(title="Voice Scheduler API")

try:
    from calendar_scheduler import CalendarService
    calendar = CalendarService()
    logger.info("CalendarService imported successfully")
except ImportError as e:
    logger.error(f"Failed to import CalendarService: {e}")
    logger.error(f"Python path is: {sys.path}")
    logger.error(f"Available files: {os.listdir('.')}")
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
    Main webhook endpoint for VAPI tool calls
    Expected payload from VAPI:
    {
        "message": {
            "type": "tool-calls",
            "toolCalls": [
                {
                    "id": "call_P95MWy6TljRomJ1Tdis5QC8W",
                    "type": "function",
                    "function": {
                        "name": "schedule_meeting",
                        "arguments": {
                            "userName": "John Doe",
                            "meetingDate": "2024-12-15",
                            "meetingTime": "14:30",
                            "meetingTitle": "Project Kickoff"
                        }
                    }
                }
            ]
        }
    }
    """
    try:
        data = await request.json()
        logger.info(f"Webhook received: {data.get('message', {}).get('type')}")
        
        message = data.get("message", {})
        message_type = message.get("type")
        
        if message_type == "tool-calls":
            tool_calls = message.get("toolCalls", [])
            
            if not tool_calls:
                logger.info("No tool calls in message")
                return JSONResponse({"ok": True})
            
            results = []
            
            for tool_call in tool_calls:
                tool_call_id = tool_call.get("id")
                function_data = tool_call.get("function", {})
                function_name = function_data.get("name")
                arguments = function_data.get("arguments", {})
                
                logger.info(f"Processing tool call: {function_name}, ID: {tool_call_id}")
                
                if function_name == "schedule_meeting":
                    if isinstance(arguments, str):
                        try:
                            arguments = json.loads(arguments)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse arguments: {e}")
                            results.append({
                                "toolCallId": tool_call_id,
                                "result": f"Error parsing arguments: {str(e)}"
                            })
                            continue
                    
                    logger.info(f"Meeting details: {arguments}")
                    
                    required_fields = ["userName", "meetingDate", "meetingTime", "meetingTitle"]
                    missing_fields = [field for field in required_fields if field not in arguments]
                    
                    if missing_fields:
                        logger.error(f"Missing fields: {missing_fields}")
                        results.append({
                            "toolCallId": tool_call_id,
                            "result": f"Missing required fields: {missing_fields}"
                        })
                        continue
                    
                    if calendar is None:
                        logger.error("CalendarService not available")
                        results.append({
                            "toolCallId": tool_call_id,
                            "result": "Calendar service not available"
                        })
                        continue
                    
                    try:
                        event = calendar.create_event({
                            "name": arguments["userName"],
                            "date": arguments["meetingDate"],
                            "time": arguments["meetingTime"],
                            "title": arguments["meetingTitle"]
                        })
                        
                        logger.info(f"Calendar event created: {event}")
                        
                        success_message = f"Meeting scheduled successfully for {arguments['userName']} on {arguments['meetingDate']} at {arguments['meetingTime']}. Title: {arguments['meetingTitle']}"
                        if event.get('id'):
                            success_message += f". Event ID: {event.get('id')}"
                        
                        results.append({
                            "toolCallId": tool_call_id,
                            "result": success_message
                        })
                        
                    except Exception as e:
                        logger.error(f"Failed to create calendar event: {str(e)}")
                        results.append({
                            "toolCallId": tool_call_id,
                            "result": f"Error creating calendar event: {str(e)}"
                        })
            
            return JSONResponse({"results": results})
        
        elif message_type in ["assistant.started", "status-update", "speech-update", "transcript", "conversation-update"]:
            logger.info(f"Acknowledging message type: {message_type}")
            return JSONResponse({"ok": True})
        
        elif message_type == "function-call":
            function_call = message.get("functionCall", {})
            function_name = function_call.get("name")
            tool_call_id = function_call.get("toolCallId")
            arguments = function_call.get("arguments", {})
            
            logger.info(f"Legacy function call: {function_name}, ID: {tool_call_id}")
            
            if function_name == "schedule_meeting":
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
                    
                    success_message = f"Meeting scheduled successfully for {arguments['userName']} on {arguments['meetingDate']} at {arguments['meetingTime']}. Title: {arguments['meetingTitle']}"
                    if event.get('id'):
                        success_message += f". Event ID: {event.get('id')}"
                    
                    return JSONResponse({
                        "results": [{
                            "toolCallId": tool_call_id,
                            "result": success_message
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
        
        return JSONResponse({"ok": True})
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        return JSONResponse({"error": str(e)})

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

@app.get("/debug")
async def debug():
    """Debug endpoint to see what's happening on Vercel"""
    import os
    import sys
    
    return {
        "python_path": sys.path,
        "current_dir": os.getcwd(),
        "files_in_current": os.listdir('.'),
        "service_account_env_set": "SERVICE_ACCOUNT_JSON" in os.environ,
        "calendar_service_file_exists": os.path.exists('calendar_scheduler.py'),
        "calendar_service_import_attempted": calendar is not None,
        "calendar_service_available": calendar is not None
    }