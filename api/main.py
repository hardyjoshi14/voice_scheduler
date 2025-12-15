import sys
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "API is running", "status": "ok"}

@app.get("/health")
async def health():
    logger.info("Health endpoint called")
    return {"status": "healthy"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Webhook received: {data}")
        return JSONResponse({"ok": True, "message": "webhook received"})
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return JSONResponse({"ok": True})

# ⚠️ CRITICAL: This is the entry point Vercel calls
# It must be named 'handler' and take (event, context) arguments
def handler(event, context):
    """
    Vercel serverless function handler.
    This wraps the FastAPI app for Vercel's environment.
    """
    from mangum import Mangum
    
    # Create Mangum adapter for FastAPI
    mangum_app = Mangum(app)
    
    # Call the Mangum handler with the Vercel event
    return mangum_app(event, context)