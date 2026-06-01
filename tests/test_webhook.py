import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_webhook_returns_accepted() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/webhook",
            json={
                "conversation_id": "conv_123",
                "message_id": "msg_456",
                "customer_phone": "+5521999999999",
                "text": "Quero negociar minha dívida",
            },
        )

    assert response.status_code == 202
    assert response.json() == {
        "status": "accepted",
        "message_id": "msg_456",
    }


@pytest.mark.asyncio
async def test_webhook_rejects_invalid_payload() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/webhook",
            json={
                "conversation_id": "",
                "message_id": "msg_456",
                "customer_phone": "+5521999999999",
                "text": "",
            },
        )

    assert response.status_code == 422