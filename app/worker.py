import asyncio
import logging

from app.queue import message_queue
from app.services.llm_service import generate_llm_response
from app.services.outbound_service import send_outbound_message

logger = logging.getLogger(__name__)


async def process_messages() -> None:
    while True:
        message = await message_queue.get()

        try:
            logger.info(
                "message_processing_started",
                extra={
                    "conversation_id": message.conversation_id,
                    "message_id": message.message_id,
                },
            )

            llm_response = await generate_llm_response(message.text)

            await send_outbound_message(
                conversation_id=message.conversation_id,
                customer_phone=message.customer_phone,
                message=llm_response,
            )

            logger.info(
                "message_processed",
                extra={
                    "conversation_id": message.conversation_id,
                    "message_id": message.message_id,
                },
            )
        except Exception:
            logger.exception(
                "message_not_processed",
                extra={
                    "conversation_id": message.conversation_id,
                    "message_id": message.message_id,
                },
            )
        finally:
            message_queue.task_done()


def start_worker() -> asyncio.Task[None]:
    return asyncio.create_task(process_messages())