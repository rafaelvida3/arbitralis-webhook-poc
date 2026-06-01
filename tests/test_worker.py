import pytest

from app.queue import dead_letter_queue
from app.schemas import WebhookMessage
from app.worker import process_message_with_retries


async def fake_generate_llm_response(text: str) -> str:
    return f"Fake response for: {text}"


async def fake_send_outbound_message(
    conversation_id: str,
    customer_phone: str,
    message: str,
) -> None:
    _ = conversation_id
    _ = customer_phone
    _ = message


async def fake_generate_llm_error(text: str) -> str:
    _ = text

    raise RuntimeError("Forced test error")


@pytest.mark.asyncio
async def test_worker_processes_valid_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.worker.generate_llm_response",
        fake_generate_llm_response,
    )
    monkeypatch.setattr(
        "app.worker.send_outbound_message",
        fake_send_outbound_message,
    )

    message = WebhookMessage(
        conversation_id="conv_123",
        message_id="msg_456",
        customer_phone="+5521999999999",
        text="Quero negociar minha dívida",
    )

    await process_message_with_retries(message)

    assert dead_letter_queue.empty()


@pytest.mark.asyncio
async def test_worker_sends_failed_message_to_dead_letter_queue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.worker.generate_llm_response",
        fake_generate_llm_error,
    )

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