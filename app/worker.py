import asyncio
import logging

from app.queue import dead_letter_queue, message_queue
from app.schemas import WebhookMessage
from app.services.llm_service import generate_llm_response
from app.services.outbound_service import send_outbound_message

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


async def process_single_message(message: WebhookMessage) -> None:
    llm_response = await generate_llm_response(message.text)

    await send_outbound_message(
        conversation_id=message.conversation_id,
        customer_phone=message.customer_phone,
        message=llm_response,
    )


async def process_message_with_retries(message: WebhookMessage) -> None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                "message_processing_started",
                extra={
                    "conversation_id": message.conversation_id,
                    "message_id": message.message_id,
                    "attempt": attempt,
                },
            )

            await process_single_message(message)

            logger.info(
                "message_processed",
                extra={
                    "conversation_id": message.conversation_id,
                    "message_id": message.message_id,
                    "attempt": attempt,
                },
            )

            return
        except Exception:
            logger.exception(
                "message_processing_failed",
                extra={
                    "conversation_id": message.conversation_id,
                    "message_id": message.message_id,
                    "attempt": attempt,
                },
            )

    await dead_letter_queue.put(message)

    logger.error(
        "message_sent_to_dead_letter_queue",
        extra={
            "conversation_id": message.conversation_id,
            "message_id": message.message_id,
            "attempts": MAX_RETRIES,
        },
    )


async def process_messages() -> None:
    while True:
        message = await message_queue.get()

        try:
            await process_message_with_retries(message)
        finally:
            message_queue.task_done()


def start_worker() -> asyncio.Task[None]:
    return asyncio.create_task(process_messages())