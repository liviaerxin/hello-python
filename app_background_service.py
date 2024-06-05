from fastapi import FastAPI
import asyncio
import os

app = FastAPI()


class BackgroundService:
    def __init__(self, loop: asyncio.AbstractEventLoop, tasks: list):
        self.loop = loop
        self.running = False

    async def work(self):
        print(f"Start background service")
        while True:
            print(f"Run background service...")
            # Sleep for 1 second
            await asyncio.sleep(1)

    async def start(self):
        self.task = self.loop.create_task(self.work())

    async def stop(self):
        self.task.cancel()
        try:
            await self.task
        except asyncio.CancelledError:
            print("Clean up background service")


service = BackgroundService(asyncio.get_running_loop())


@app.on_event("startup")
async def startup():
    print(f"PID[{os.getpid()}] app startup")
    # schedule a task on main loop
    await service.start()


@app.on_event("shutdown")
async def shutdown():
    # close ProcessPoolExecutor
    print(f"PID[{os.getpid()}] app shutdown")
    await service.stop()


@app.post("/")
async def hello():
    return {"value": f"hello world [{service.task.done()}] [{service.task.get_name()}]"}
