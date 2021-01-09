import enum
from pydantic import BaseModel


class EventType(enum.Enum):
    pass


class WebhookEvent(BaseModel):
    pass
