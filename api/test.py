from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Test endpoint working"}

@app.get("/health")
async def health():
    return {"status": "healthy"}