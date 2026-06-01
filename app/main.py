from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from app.logging_config import configure_logging
from app.queue import message_queue
from app.schemas import WebhookAcceptedResponse, WebhookMessage
from app.worker import start_worker


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    worker_task = start_worker()

    yield

    worker_task.cancel()

configure_logging()

app = FastAPI(
    title="Arbitralis Webhook PoC",
    lifespan=lifespan,
)


@app.post(
    "/webhook",
    response_model=WebhookAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def receive_webhook(message: WebhookMessage) -> WebhookAcceptedResponse:
    await message_queue.put(message)

    return WebhookAcceptedResponse(
        status="accepted",
        message_id=message.message_id,
    )