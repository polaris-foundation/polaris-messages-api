from enum import Enum
from typing import Dict, Optional

from faker import Faker


class MessageTypes(Enum):
    GENERAL = 0
    DOSAGE = 1
    DIETARY = 2
    FEEDBACK = 3
    CALLBACK = 5
    ACTIVATION_CODE = 6
    RED_ALERT = 7
    AMBER_ALERT = 8
    GREY_ALERT = 9
    CLEAR_ALERTS = 10


def get_message_body(**kwargs: Optional[Dict]) -> Dict:
    fake: Faker = Faker()
    default_body: dict = {
        "sender": fake.uuid4(),
        "sender_type": "clinician",
        "receiver": fake.uuid4(),
        "receiver_type": "patient",
        "message_type": {"value": MessageTypes.GENERAL.value},
        "content": fake.sentence(),
    }
    return {**default_body, **kwargs}
