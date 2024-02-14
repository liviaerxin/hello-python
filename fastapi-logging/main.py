from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)
app = FastAPI()

@app.get("/")
async def func():
    logger.info(f"request / endpoint!")
    return {"message": "hello world!"}
