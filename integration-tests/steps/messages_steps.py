from typing import Any, Dict

from behave import step
from behave.runner import Context
from clients import messages_client
from helpers import message as message_helper
from jose import jwt as jose_jwt
from requests import Response


@step(
    "the {sender_type} sends ({version}) the {receiver_type} a {message_type} message"
)
def send_patient_message(
    context: Context,
    receiver_type: str,
    sender_type: str,
    message_type: str,
    version: str,
) -> None:

    special_user_type = None
    if receiver_type == "bad_user_type":
        special_user_type = receiver_type
        receiver_type = "patient"

    sender_jwt: str = (
        context.clinician_jwt if sender_type == "clinician" else context.patient_jwt
    )
    receiver_jwt: str = (
        context.clinician_jwt if receiver_type == "clinician" else context.patient_jwt
    )

    decode_options: dict = {
        "verify_signature": False,
        "verify_aud": False,
        "verify_sub": False,
    }
    sender_jwt_decoded: dict = jose_jwt.decode(
        token=sender_jwt, key=None, options=decode_options
    )
    receiver_jwt_decoded: dict = jose_jwt.decode(
        token=receiver_jwt, key=None, options=decode_options
    )

    body: Dict = message_helper.get_message_body(
        **{
            "sender_type": sender_type,
            "sender": sender_jwt_decoded["metadata"][f"{sender_type}_id"],
            "receiver_type": special_user_type or receiver_type,
            "receiver": receiver_jwt_decoded["metadata"][f"{receiver_type}_id"],
            "message_type": {"value": message_helper.MessageTypes[message_type].value},
        }
    )
    context.message_body = body
    response: Response
    if version == "v2":
        response = messages_client.send_message_v2(
            jwt=sender_jwt, body=body, headers={"X-Location-Ids": "loc1,loc2"}
        )
    else:
        response = messages_client.send_message(
            jwt=sender_jwt, body=body, headers={"X-Location-Ids": "loc1,loc2"}
        )
    response.raise_for_status()

    response_json: dict = response.json()
    assert "uuid" in response_json
    context.api_message_body = response_json


@step("the API result body matches that of the sent message")
def assert_message_sent_returned_by_api(context: Context) -> None:
    assert context.message_body["sender"] == context.api_message_body["sender"]
    assert context.message_body["receiver"] == context.api_message_body["receiver"]
    assert context.message_body["content"] == context.api_message_body["content"]


@step("The message {can_or_can_not} be seen in all messages")
def assert_message_seen_in_all_messages(context: Context, can_or_can_not: str) -> None:
    response: Response = messages_client.get_all_messages(jwt=context.system_jwt)
    response.raise_for_status()

    all_messages: list = [message["uuid"] for message in response.json()]
    if can_or_can_not == "can not":
        assert context.api_message_body["uuid"] not in all_messages
    else:
        assert context.api_message_body["uuid"] in all_messages


@step("the message gets deleted")
def delete_message(context: Context) -> None:
    response: Response = messages_client.delete_message(
        jwt=context.system_jwt, uuid=context.api_message_body["uuid"]
    )
    response.raise_for_status()


@step("{user} can retrieve the message")
def retrieve_message_by_sender_recipient(context: Context, user: str) -> None:
    user_r: str = user.replace(" ", "_")
    caller_method = getattr(messages_client, f"get_messages_by_{user_r}")

    if user in ["sender and receiver", "sender or receiver"]:
        for jwt_type in ["sender", "receiver"]:
            user_type: str = context.message_body[f"{jwt_type}_type"]
            jwt: str = getattr(context, f"{user_type}_jwt")

            common_args: dict = {
                "caller_method": caller_method,
                "jwt": jwt,
                "message_uuid": context.api_message_body["uuid"],
            }

            if user == "sender and receiver":
                method_specific_args: dict = {
                    "sender_uuid": context.api_message_body["sender"],
                    "receiver_uuid": context.api_message_body["receiver"],
                }
            else:
                method_specific_args = {"uuid": context.api_message_body[jwt_type]}

            _assert_message_can_be_read(**{**common_args, **method_specific_args})
    else:
        user_type = context.message_body[f"{user}_type"]
        jwt = getattr(context, f"{user_type}_jwt")
        _assert_message_can_be_read(
            caller_method=caller_method,
            jwt=jwt,
            uuid=context.message_body[user],
            message_uuid=context.api_message_body["uuid"],
        )


def _assert_message_can_be_read(**kwargs: Any) -> None:
    caller_method = kwargs["caller_method"]
    response: Response = caller_method(**kwargs)
    response.raise_for_status()

    all_messages: list = [message["uuid"] for message in response.json()]
    assert kwargs["message_uuid"] in all_messages
