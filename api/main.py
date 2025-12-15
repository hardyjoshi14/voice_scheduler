from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import json

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello from Vercel", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Just acknowledge receipt
        return JSONResponse({"ok": True, "message": "webhook received"})
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return JSONResponse({"ok": True})

# Handler for Vercel (optional)
async def handler(request: Request):
    return await webhook(request)