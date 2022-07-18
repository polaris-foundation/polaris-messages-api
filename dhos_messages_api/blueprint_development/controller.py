from typing import Dict, List

from flask_batteries_included.sqldb import db

from dhos_messages_api.models.message import Message
from dhos_messages_api.models.message_type import MessageType


def reset_database() -> None:
    session = db.session
    session.execute("TRUNCATE TABLE message")
    session.commit()
    session.close()


def create_messages(messages_details: List[Dict]) -> None:
    for message_details in messages_details:
        message_type_value: int = message_details.pop("message_type")["value"]
        message_type = MessageType.query.filter_by(value=message_type_value).first()
        message = Message(**message_details, message_type=message_type)
        db.session.add(message)
    db.session.commit()
