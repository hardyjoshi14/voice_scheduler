from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from calendar_scheduler import CalendarService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
calendar = CalendarService()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Webhook endpoint is running"}

@app.post("/api/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received webhook: {json.dumps(data, indent=2)}")
        
        message = data.get("message", {})
        message_type = message.get("type")
        
        logger.info(f"Message type: {message_type}")
        
        if message_type == "conversation-update":
            return await handle_conversation_update(data)
        elif message_type in ["assistant.started", "status-update", "speech-update"]:
            return JSONResponse(content={"ok": True}, status_code=200)
        elif message_type == "function-call":
            return JSONResponse(content={"ok": True}, status_code=200)
        else:
            return JSONResponse(content={"ok": True}, status_code=200)
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JSONResponse(content={"ok": True}, status_code=200)
    except Exception as e:
        logger.exception(f"Unexpected error in webhook: {e}")
        return JSONResponse(content={"ok": True}, status_code=200)

async def handle_conversation_update(data: Dict[str, Any]) -> JSONResponse:
    """Handle conversation-update messages specifically"""
    try:
        call = data.get("call", {})
        variables = call.get("variableValues") or {}
        
        logger.info(f"Variables received: {variables}")
        
        required = ["userName", "meetingDate", "meetingTime"]
        
        missing = [k for k in required if not variables.get(k)]
        if missing:
            logger.info(f"Missing variables: {missing}")
            return JSONResponse(content={"ok": True}, status_code=200)
        
        event = calendar.create_event({
            "name": variables["userName"],
            "date": variables["meetingDate"],
            "time": variables["meetingTime"],
            "title": variables.get("meetingTitle", "Meeting")
        })
        
        logger.info(f"Created calendar event: {event}")
        
        return JSONResponse(content={
            "success": True,
            "event": event
        }, status_code=200)
        
    except Exception as e:
        logger.exception(f"Error handling conversation update: {e}")
        return JSONResponse(content={"ok": True}, status_code=200)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)