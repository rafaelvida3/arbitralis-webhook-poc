import logging

logger = logging.getLogger(__name__)


async def send_outbound_message(
    conversation_id: str,
    customer_phone: str,
    message: str,
) -> None:
    _ = customer_phone
    _ = message

    logger.info(
        "outbound_message_sent",
        extra={
            "conversation_id": conversation_id,
        },
    )
