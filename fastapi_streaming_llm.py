from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

# `uvicorn app_streaming_llm:app --reload`
app = FastAPI()

# Mock OpenAPI API token generation
async def generate_json():
    messages = ["Once", " upon", " a", " time", " there", " was", " an", " AI."]
    for word in messages:
        data = "event: delta" + "\n" + "data:" + json.dumps({"message": word}) + "\n\n"
        yield data
        await asyncio.sleep(0.5)

@app.get("/llm")
async def json_stream():
    return StreamingResponse(generate_json(), media_type="text/event-stream")
