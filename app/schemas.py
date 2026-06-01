from pydantic import BaseModel, Field


class WebhookMessage(BaseModel):
    conversation_id: str = Field(..., min_length=1)
    message_id: str = Field(..., min_length=1)
    customer_phone: str = Field(..., min_length=8)
    text: str = Field(..., min_length=1)


class WebhookAcceptedResponse(BaseModel):
    status: str
    message_id: str