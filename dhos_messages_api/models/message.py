from datetime import datetime
from typing import Any, Dict

from flask_batteries_included.helpers.timestamp import (
    join_timestamp,
    parse_datetime_to_iso8601,
    split_timestamp,
)
from flask_batteries_included.sqldb import ModelIdentifier, db

from dhos_messages_api.models.message_type import MessageType
from dhos_messages_api.query.softdelete import QueryWithSoftDelete


class Message(ModelIdentifier, db.Model):
    query_class = QueryWithSoftDelete

    # required
    sender = db.Column(db.String, unique=False, nullable=False, index=True)
    sender_type = db.Column(db.String, unique=False, nullable=False, index=True)
    receiver = db.Column(db.String, unique=False, nullable=False, index=True)
    receiver_type = db.Column(db.String, unique=False, nullable=False, index=True)

    content = db.Column(db.String, unique=False, nullable=False)

    # optional
    retrieved = db.Column(db.DateTime, unique=False, nullable=True, index=True)
    retrieved_tz = db.Column(db.Integer, unique=False, nullable=True)

    confirmed = db.Column(db.DateTime, unique=False, nullable=True, index=True)
    confirmed_tz = db.Column(db.Integer, unique=False, nullable=True)

    cancelled = db.Column(db.DateTime, unique=False, nullable=True, index=True)
    cancelled_tz = db.Column(db.Integer, unique=False, nullable=True)
    cancelled_by = db.Column(db.String, unique=False, nullable=True)

    confirmed_by = db.Column(db.String, unique=False, nullable=True)
    related_message = db.Column(db.String, unique=False, nullable=True)

    internal = db.Column(db.String, unique=False, nullable=True)

    # system
    deleted = db.Column(db.DateTime, unique=False, nullable=True)

    # relationship
    message_type_id = db.Column(db.Integer, db.ForeignKey("message_type.value"))
    message_type = db.relationship("MessageType", lazy="joined")

    db.Index("message_type_index", message_type_id)

    @staticmethod
    def schema() -> Dict:
        return {
            "optional": {
                "retrieved": str,
                "confirmed": str,
                "confirmed_by": str,
                "related_message": str,
                "cancelled": str,
                "cancelled_by": str,
                "internal": str,
            },
            "required": {
                "sender": str,
                "sender_type": str,
                "receiver": str,
                "receiver_type": str,
                "message_type": str,
                "content": str,
            },
            "updatable": {
                "retrieved": str,
                "confirmed": str,
                "confirmed_by": str,
                "related_message": str,
                "cancelled": str,
                "cancelled_by": str,
                "internal": str,
            },
            "builtin": {
                "created": str,
                "modified": str,
                "uuid": str,
                "created_by_": str,
                "modified_by_": str,
            },
        }

    def to_dict(self) -> Dict:
        schema = self.schema()
        message = {}
        for key in schema["required"]:
            if key == "message_type":
                message[key] = self.message_type.to_dict()
            else:
                message[key] = getattr(self, key)

        for key in schema["optional"]:
            value = getattr(self, key)
            if key in ("retrieved", "confirmed", "cancelled") and value is not None:
                value = join_timestamp(value, getattr(self, "{}_tz".format(key)))
            if value is not None or key == "confirmed":
                message[key] = value

        if self.deleted is not None:
            message["deleted"] = parse_datetime_to_iso8601(self.deleted)

        return {**message, **self.pack_identifier()}

    def delete(self) -> None:
        self.deleted = datetime.utcnow()

    def set_property(self, key: str, value: Any) -> None:
        if key == "related_message":
            if self.uuid == value:
                raise KeyError(
                    "Cannot set property related_message, "
                    "circular reference to parent."
                )
            message = Message.query.filter_by(uuid=value).first()
            if message is None:
                raise KeyError(self.invalid_value_error(key, value))

        if key == "message_type":
            original_value = value
            value = MessageType.query.filter_by(value=value).first()
            if not value:
                raise KeyError(self.invalid_value_error(key, original_value))

        if key in ["retrieved", "confirmed", "cancelled"]:
            ts, tz = split_timestamp(value)
            setattr(self, key, ts)
            setattr(self, "{}_tz".format(key), tz)
            return
        setattr(self, key, value)

    def invalid_value_error(self, key: str, value: Any) -> str:
        return "Cannot set '{}' as '{}' is an invalid value.".format(key, value)
