# main.py
from fastapi import FastAPI
import asyncio

app = FastAPI()
lock = asyncio.Lock()

counter = 0


@app.post("/limit")
async def func():
    global counter
    async with lock:
        print("Hello")
        counter = counter + 1
        await asyncio.sleep(2)
        print("bye")
        await asyncio.sleep(2)
        return {"counter": counter}


"""
Make 2 requests at a time, output from server:

INFO:     127.0.0.1:60228 - "POST /limit HTTP/1.1" 200 OK
Hello
bye
INFO:     127.0.0.1:51010 - "POST /limit HTTP/1.1" 200 OK
Hello
bye
INFO:     127.0.0.1:51022 - "POST /limit HTTP/1.1" 200 OK

Request 1:

❯ curl -X 'POST' \
  'http://127.0.0.1:8000/limit' \
  -H 'accept: application/json' \
  -d ''
{"counter":1}%

Request 2:

❯ curl -X 'POST' \
  'http://127.0.0.1:8000/limit' \
  -H 'accept: application/json' \
  -d ''
{"counter":2}%
"""
