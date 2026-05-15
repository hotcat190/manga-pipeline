import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.consumer import start_rabbitmq_consumer

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://user:password@rabbitmq:5672/")
QUEUE_NAME = os.getenv("QUEUE_NAME", "manga_processing_queue")

@asynccontextmanager
async def lifespan(app: FastAPI):
    rmq_connection = await start_rabbitmq_consumer(RABBITMQ_URL, QUEUE_NAME)
    yield
    await rmq_connection.close()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "manga-ai-worker",
        "queue": QUEUE_NAME
    }

print('Pipeline service started')

