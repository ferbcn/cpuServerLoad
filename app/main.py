import time
import json
import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List
import psutil
import asyncio
from contextlib import asynccontextmanager

from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(get_cpu_load())
    yield
    task.cancel()

app = FastAPI(title='WebsocketAPI', lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except WebSocketDisconnect:
                await self.disconnect(connection)


manager = ConnectionManager()


async def get_cpu_load():
    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        mem_percent = psutil.virtual_memory().percent
        active_conns = len(manager.active_connections)
        data = {"cpu": cpu_percent, "mem": mem_percent, "conns": active_conns}
        json_string = json.dumps(data)
        await manager.broadcast(json_string)
        await asyncio.sleep(1)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    seconds_elapsed = int(time.time() - psutil.boot_time())
    cpu_count = psutil.cpu_count()

    return templates.TemplateResponse("index.html", {"request": request, "cpu_count": cpu_count, "uptime": seconds_elapsed})


@app.websocket("/wscpu")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)


@app.get("/api-stats", response_class=JSONResponse)
async def stats():
    cpu_percent = psutil.cpu_percent(interval=1)
    mem_percent = psutil.virtual_memory().percent
    active_conns = len(manager.active_connections)
    data = {"cpu": cpu_percent, "mem": mem_percent, "conns": active_conns}
    return data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)