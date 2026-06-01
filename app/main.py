from fastapi import FastAPI, status

from app.queue import message_queue
from app.schemas import WebhookAcceptedResponse, WebhookMessage

app = FastAPI(title="Arbitralis Webhook PoC")


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