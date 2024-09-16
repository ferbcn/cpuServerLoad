import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
import psutil

app = FastAPI(title='WebsocketAPI')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Getting access token from environment variable
access_token = os.getenv("SERVER_TOKEN")


def verify_token(token: str = Depends(oauth2_scheme)):
    if not token == access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/api-stats", response_class=JSONResponse)
async def stats(token: str = Depends(verify_token)):
    cpu_percent = psutil.cpu_percent()
    mem_percent = psutil.virtual_memory().percent
    data = {"cpu": cpu_percent, "mem": mem_percent}
    return data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)