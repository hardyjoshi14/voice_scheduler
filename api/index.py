from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Scheduler API")

# Add CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Voice Scheduler API", "status": "ok", "framework": "FastAPI"}

@app.get("/health")
async def health():
    return {"status": "healthy", "framework": "FastAPI"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Webhook received: {data.get('message', {}).get('type')}")
        
        # TODO: Add your CalendarService logic here
        
        return JSONResponse({
            "ok": True, 
            "message": "Webhook processed",
            "framework": "FastAPI"
        })
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse({"ok": True})

# ⚠️ IMPORTANT: For Vercel to recognize this as a serverless function
# Export the app with the name 'app'
# Vercel's Python runtime automatically detects FastAPI apps