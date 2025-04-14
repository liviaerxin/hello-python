from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import time

# `uvicorn fastapi_streaming_sse:app --reload`
app = FastAPI()

# This function is an async generator that will yield data over time
async def event_stream():
    # Simulate an ongoing process (e.g., data generation or model streaming)
    for i in range(10):
        # Yield data in the SSE format: "data: <message>\n\n"
        yield f"data: Message {i}\n\n"
        await asyncio.sleep(1)  # Simulate delay between messages

# SSE endpoint that streams data
@app.get("/sse")
async def sse():
    return StreamingResponse(event_stream(), media_type="text/plain")