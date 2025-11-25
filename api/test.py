"""
Simple test endpoint to verify Vercel serverless functions work.
"""

from mangum import Mangum
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def test():
    return {
        "status": "success",
        "message": "Vercel serverless function is working!",
        "service": "GhostRevive API"
    }

@app.post("/")
async def test_post():
    return {
        "status": "success",
        "message": "POST endpoint working!",
        "service": "GhostRevive API"
    }

# Create Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
