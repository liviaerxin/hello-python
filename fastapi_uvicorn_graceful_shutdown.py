"""
Starting up server,
```sh
uvicorn fastapi_uvicorn_graceful_shutdown:app
```

Testing by `curl`,
```sh
curl http://localhost:8000/hello
curl http://localhost:8000/shutdown
```
"""

import os
import signal
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/hello")
def hello():
    return {"message": "Hello, world!"}


@app.get("/shutdown")
def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return HTTPException(status_code=200, detail="Server shutting down...")


@app.on_event("shutdown")
def on_shutdown():
    print("Server shutting down...")
