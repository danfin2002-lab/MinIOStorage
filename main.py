from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from src.routers import router

from src.broker import broker

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Устанавливаем соединение
    print("Starting broker...")
    await broker.start()
    print("Broker started")
    yield
    print("Stopping broker")
    await broker.stop()
    print("Broker stoped")

app = FastAPI(lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="127.0.0.1", port=8000)