from enum import Enum
from typing import Dict, List, Optional

from flask import g
from flask_batteries_included.config import is_production_environment
from flask_batteries_included.sqldb import db, generate_uuid
from she_logging import logger

from dhos_messages_api.helper.security import (
    get_clinician_locations,
    user_type_to_validate,
)
from dhos_messages_api.models.message import Message
from dhos_messages_api.models.message_type import MessageType


class DhosMessageType(Enum):
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


def create_message(message_details: Dict) -> Dict:
    logger.debug("Creating message", extra={"message_data": message_details})

    insert = Message()
    schema = Message.schema()

    for sent_property in message_details:
        if sent_property in schema["required"]:
            continue
        if sent_property in schema["optional"]:
            continue
        if sent_property in schema["builtin"] and not is_production_environment():
            continue
        raise KeyError("Property '{}' not found in schema".format(sent_property))

    for required_property in schema["required"]:
        if (
            required_property not in message_details
            or message_details[required_property] is None
            or len(str(message_details[required_property])) == 0
        ):
            raise KeyError(
                "Property '{}' must contain a valid value".format(required_property)
            )

    message_type: Optional[MessageType] = None
    for sent_property in message_details:
        if len(message_details[sent_property]) == 0:
            raise KeyError(
                "Empty fields should not be sent, property '{}' is empty".format(
                    sent_property
                )
            )
        if sent_property == "message_type":
            query_result: MessageType = MessageType.query.filter_by(
                value=message_details[sent_property]["value"]
            ).first()
            if query_result:
                message_type = query_result
            else:
                raise KeyError(
                    "Property 'message_type' must contain a valid value, {} received".format(
                        message_details[sent_property]["value"]
                    )
                )
        else:
            insert.set_property(sent_property, message_details[sent_property])

    insert.uuid = generate_uuid()
    insert.message_type = message_type

    db.session.add(insert)
    db.session.commit()

    return insert.to_dict()


def get_message_by_uuid(message_uuid: str) -> Dict:
    logger.debug("Getting message by UUID '%s'", message_uuid)
    message = Message.query.filter_by(uuid=message_uuid).first_or_404()
    return message.to_dict()


def get_messages_by_sender_uuid(sender_uuid: str) -> List[Dict]:
    logger.debug("Getting messages by sender ID '%s'", sender_uuid)
    user_type = user_type_to_validate(sender_uuid, g.jwt_claims)
    all_messages = Message.query.filter_by(
        sender=sender_uuid, sender_type=user_type
    ).order_by(Message.created.desc())
    all_message_data: List[Dict] = [message.to_dict() for message in all_messages]
    logger.debug(
        "Found %d messages with sender ID '%s'",
        len(all_message_data),
        sender_uuid,
    )
    return all_message_data


def get_messages_by_receiver_uuid(receiver_uuid: str) -> List[Dict]:
    logger.debug("Getting messages by receiver ID '%s'", receiver_uuid)
    all_messages = Message.query.filter_by(receiver=receiver_uuid).order_by(
        Message.created.desc()
    )

    user_type = user_type_to_validate(receiver_uuid, g.jwt_claims)
    if user_type:
        all_messages = all_messages.filter_by(receiver_type=user_type)

    all_message_data: List[Dict] = [message.to_dict() for message in all_messages]
    logger.debug(
        "Found %d messages with receiver ID '%s'",
        len(all_message_data),
        receiver_uuid,
    )
    return all_message_data


def get_active_messages_by_sender_uuid(sender_uuid: str) -> List[Dict]:
    logger.debug("Getting active messages by sender ID '%s'", sender_uuid)
    user_type = user_type_to_validate(sender_uuid, g.jwt_claims)
    all_messages = Message.query.filter(
        (Message.sender_type == user_type)
        & (Message.sender == sender_uuid)
        & (
            (Message.confirmed.is_(None))
            | (Message.message_type_id == DhosMessageType.CALLBACK.value)
        )
    )
    all_message_data: List[Dict] = [message.to_dict() for message in all_messages]
    logger.debug(
        "Found %d active messages with sender ID '%s'",
        len(all_message_data),
        sender_uuid,
    )
    return all_message_data


def get_active_messages_by_receiver_uuid(receiver_uuid: str) -> List[Dict]:
    logger.debug("Getting active messages by receiver ID '%s'", receiver_uuid)
    user_type = user_type_to_validate(receiver_uuid, g.jwt_claims)
    all_messages = Message.query.filter(
        (Message.receiver_type == user_type)
        & (Message.receiver == receiver_uuid)
        & (
            (Message.confirmed.is_(None))
            | (Message.message_type_id == DhosMessageType.CALLBACK.value)
        )
    )
    all_message_data: List[Dict] = [message.to_dict() for message in all_messages]
    logger.debug(
        "Found %d active messages with receiver ID '%s'",
        len(all_message_data),
        receiver_uuid,
    )
    return all_message_data


def get_active_callback_messages_by_receiver_uuid(receiver_uuid: str) -> List[Dict]:
    logger.debug("Getting active callback messages by receiver ID '%s'", receiver_uuid)
    user_type = user_type_to_validate(receiver_uuid, g.jwt_claims)
    all_messages = Message.query.filter(
        (
            (Message.receiver_type == user_type)
            & (Message.receiver == receiver_uuid)
            & (Message.confirmed.is_(None))
            & (Message.cancelled.is_(None))
        )
        & (Message.message_type_id == DhosMessageType.CALLBACK.value)
    )
    all_message_data: List[Dict] = [message.to_dict() for message in all_messages]
    logger.debug(
        "Found %d active callback messages with receiver ID '%s'",
        len(all_message_data),
        receiver_uuid,
    )
    return all_message_data


def get_messages_by_sender_uuid_or_receiver_uuid(uuid: str) -> List[Dict]:
    logger.debug("Getting messages by sender or receiver ID '%s'", uuid)

    user_type = user_type_to_validate(uuid, g.jwt_claims)

    all_messages: List[Message]
    if user_type:
        all_messages = get_all_from_specific_user_and_id(uuid, user_type)
    else:
        if g.jwt_claims.get("clinician_id"):
            all_messages = get_all_from_unique_id_filtered_to_clinician(uuid)
        elif g.jwt_claims.get("system_id"):
            all_messages = Message.query.filter(
                ((Message.sender == uuid)) | ((Message.receiver == uuid))
            )

    all_message_data: List[Dict] = [message.to_dict() for message in all_messages]
    logger.debug(
        "Found %d messages with sender or receiver ID '%s'",
        len(all_message_data),
        uuid,
    )
    return all_message_data


def get_all_from_unique_id_filtered_to_clinician(unique_id: str) -> List[Message]:
    """
    Returns messages:
    - sent or received by this id, if the other party is the clinician making the request
    - sent or received by this id, if the other party is an allowed location
    - sent or received by this id, if this id is a patient id

    This is the same as:
    - if the id is a patient_id:
        - _all_ messages to or from the patient
    - if the id is a clinician_id:
        - messages to or from that clinician, if the other party is the clinician who is making the request
        - messages to or from that clinician, if the other party is a location, and the user making the request has access to that location
    - if the id is a location_id:
        - messages to or from that location, if the other party is the clinician who is making the request
        - messages to or from that location, if the other party is a location, and the user making the request has access to that location
    """

    filter_ids: List[str] = get_clinician_locations()
    clinician_uuid: str = g.jwt_claims["clinician_id"]

    all_messages = Message.query.filter(
        (
            (Message.sender == unique_id)
            & (Message.receiver == clinician_uuid)
            & (Message.receiver_type == "clinician")
        )
        | (
            (Message.receiver == unique_id)
            & (Message.sender == clinician_uuid)
            & (Message.sender_type == "clinician")
        )
        | (
            (Message.sender == unique_id)
            & (Message.receiver.in_(filter_ids))
            & (Message.receiver_type == "location")
        )
        | (
            (Message.receiver == unique_id)
            & (Message.sender.in_(filter_ids))
            & (Message.sender_type == "location")
        )
        | ((Message.sender == unique_id) & (Message.sender_type == "patient"))
        | ((Message.receiver == unique_id) & (Message.receiver_type == "patient"))
    )

    return all_messages


def get_all_from_specific_user_and_id(unique_id: str, user_type: str) -> List[Message]:
    all_messages = Message.query.filter(
        (
            (Message.sender == unique_id)
            & (Message.sender_type == user_type)
            & (Message.message_type_id != DhosMessageType.RED_ALERT.value)
            & (Message.message_type_id != DhosMessageType.AMBER_ALERT.value)
            & (Message.message_type_id != DhosMessageType.GREY_ALERT.value)
        )
        | (
            (Message.receiver == unique_id)
            & (Message.receiver_type == user_type)
            & (Message.message_type_id != DhosMessageType.RED_ALERT.value)
            & (Message.message_type_id != DhosMessageType.AMBER_ALERT.value)
            & (Message.message_type_id != DhosMessageType.GREY_ALERT.value)
        )
    )
    return all_messages


def get_messages_by_sender_uuid_and_receiver_uuid(
    sender_uuid: str, receiver_uuid: str
) -> List[Dict]:
    logger.debug(
        "Getting messages by sender ID '%s' AND receiver ID '%s'",
        sender_uuid,
        receiver_uuid,
    )
    all_messages = Message.query.filter_by(
        receiver=receiver_uuid, sender=sender_uuid
    ).order_by(Message.created.desc())

    all_message_data: List[Dict] = [message.to_dict() for message in all_messages]
    logger.debug(
        "Found %d messages with specified sender and receiver IDs",
        len(all_message_data),
    )
    return all_message_data


def get_active_messages_by_sender_uuid_and_receiver_uuid(
    sender_uuid: str, receiver_uuid: str
) -> List[Dict]:
    logger.debug(
        "Getting active messages by sender ID '%s' AND receiver ID '%s'",
        sender_uuid,
        receiver_uuid,
    )
    all_messages = Message.query.filter(
        (Message.confirmed.is_(None))
        | (Message.message_type_id == DhosMessageType.CALLBACK.value)
        & (Message.receiver == receiver_uuid)
        & (Message.sender == sender_uuid)
    ).order_by(Message.created.desc())

    all_message_data: List[Dict] = [message.to_dict() for message in all_messages]
    logger.debug(
        "Found %d active messages with specified sender and receiver IDs",
        len(all_message_data),
    )
    return all_message_data


def update_message(message_uuid: str, message_details: Dict) -> Dict:
    logger.debug(
        "Updating message with UUID %s",
        message_uuid,
        extra={"message_data": message_details},
    )
    message_db = Message.query.filter_by(uuid=message_uuid).first_or_404()
    has_one_or_more_values = False

    for property_to_update in message_details:
        has_one_or_more_values = True
        message_db.set_property(property_to_update, message_details[property_to_update])

    if not has_one_or_more_values:
        raise KeyError("valid update parameters not found.")

    db.session.commit()
    return message_db.to_dict()


def get_active_callback_messages_for_patients(patient_list: Dict) -> Dict:
    messages = Message.query.filter(
        (Message.confirmed.is_(None))
        & (Message.cancelled.is_(None))
        & (Message.message_type_id == DhosMessageType.CALLBACK.value)
        & (Message.sender.in_(patient_list))
    ).distinct(Message.sender)
    callbacks: Dict = {}
    for msg in messages:
        callbacks[msg.sender] = msg.to_dict()

    return callbacks
