"""
Pure FastAPI app - tested separately
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Voice Scheduler FastAPI")

@app.get("/fastapi-health")
async def health():
    logger.info("FastAPI health endpoint called")
    return {"status": "healthy", "framework": "FastAPI"}

@app.get("/fastapi")
async def root():
    return {"message": "FastAPI endpoint", "status": "ok"}

@app.post("/fastapi-webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"FastAPI webhook: {data.get('message', {}).get('type')}")
        return JSONResponse({"ok": True, "framework": "FastAPI"})
    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse({"ok": True})

# Export for Vercel
application = app  # Vercel looks for this