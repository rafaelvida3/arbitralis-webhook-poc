import pytest

from app.queue import dead_letter_queue
from app.schemas import WebhookMessage
from app.worker import process_message_with_retries


@pytest.mark.asyncio
async def test_worker_processes_valid_message() -> None:
    message = WebhookMessage(
        conversation_id="conv_123",
        message_id="msg_456",
        customer_phone="+5521999999999",
        text="Quero negociar minha dívida",
    )

    await process_message_with_retries(message)

    assert dead_letter_queue.empty()


@pytest.mark.asyncio
async def test_worker_sends_failed_message_to_dead_letter_queue() -> None:
    message = WebhookMessage(
        conversation_id="conv_error",
        message_id="msg_error",
        customer_phone="+5521999999999",
        text="force_llm_error",
    )

    await process_message_with_retries(message)

    failed_message = await dead_letter_queue.get()

    assert failed_message.message_id == "msg_error"

    dead_letter_queue.task_done()