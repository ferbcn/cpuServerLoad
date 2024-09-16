import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import psutil


app = FastAPI(title='WebsocketAPI')


@app.get("/api-stats", response_class=JSONResponse)
async def stats():
    cpu_percent = psutil.cpu_percent(interval=1)
    mem_percent = psutil.virtual_memory().percent
    data = {"cpu": cpu_percent, "mem": mem_percent}
    return data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)