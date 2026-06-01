import asyncio

from app.schemas import WebhookMessage

message_queue: asyncio.Queue[WebhookMessage] = asyncio.Queue()
dead_letter_queue: asyncio.Queue[WebhookMessage] = asyncio.Queue()
