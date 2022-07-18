import datetime
from typing import Any, Dict

from behave import step
from behave.runner import Context
from clients import messages_client
from helpers import jwt as jwt_helper
from helpers import message as message_helper
from jose import jwt as jose_jwt
from requests import Response
from she_logging import logger


@step(
    "clinician {can_or_can_not} see the message in the list of active callbacks for patients"
)
def message_in_active_callbacks_for_patients(
    context: Context, can_or_can_not: str
) -> None:
    response: Response = messages_client.retrieve_active_callbacks_for_list_of_patients(
        jwt=context.clinician_jwt, patient_uuids=[context.message_body["sender"]]
    )
    response.raise_for_status()

    all_messages: dict = response.json()
    if can_or_can_not == "can not":
        assert context.message_body["sender"] not in all_messages
    else:
        assert context.message_body["sender"] in all_messages
        assert (
            context.api_message_body["uuid"]
            == all_messages[context.message_body["sender"]]["uuid"]
        )


@step("the {user} {can_or_can_not} see the message in the list of active messages")
def assert_clinician_sees_message_in_active_messages(
    context: Context, user: str, can_or_can_not: str
) -> None:
    response: Response = messages_client.get_active_messages_by_receiver(
        jwt=jwt_helper.get_cached_token_for_user_type(context=context, user_type=user),
        uuid=context.message_body["receiver"],
    )
    response.raise_for_status()
    all_messages = [message["uuid"] for message in response.json()]

    if can_or_can_not == "can not":
        assert context.api_message_body["uuid"] not in all_messages
    else:
        assert context.api_message_body["uuid"] in all_messages


@step("the {user} {can_or_can_not} see the message in the list of received messages")
def assert_user_sees_message_in_received_messages(
    context: Context, user: str, can_or_can_not: str
) -> None:
    response: Response = messages_client.get_messages_by_receiver(
        jwt=jwt_helper.get_cached_token_for_user_type(context=context, user_type=user),
        uuid=context.message_body["receiver"],
    )
    response.raise_for_status()
    all_messages = [message["uuid"] for message in response.json()]

    if can_or_can_not == "can not":
        assert context.api_message_body["uuid"] not in all_messages
    else:
        assert context.api_message_body["uuid"] in all_messages


@step("the {user} confirms the message")
def confirm_message(context: Context, user: str) -> None:
    response: Response = messages_client.update_message(
        jwt=jwt_helper.get_cached_token_for_user_type(context=context, user_type=user),
        uuid=context.api_message_body["uuid"],
        body={"confirmed": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%S.%fZ")},
    )
    response.raise_for_status()
