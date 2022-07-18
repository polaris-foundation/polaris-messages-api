import random
import string
import time
from typing import Dict

from behave import given, step, then, when
from behave.runner import Context
from clients import messages_client
from helpers import message as message_helper
from jose import jwt as jose_jwt


@given("the database is empty")
def reset_db(context: Context) -> None:
    messages_client.reset_db(jwt=context.system_jwt)


@given("the database is seeded with {number_messages:d} messages")
def seed_db_with_messages(context: Context, number_messages: int) -> None:
    context.number_messages = number_messages
    sender_jwt: str = context.clinician_jwt
    receiver_jwt: str = context.patient_jwt
    decode_options: dict = {
        "verify_signature": False,
        "verify_aud": False,
        "verify_sub": False,
    }
    sender_jwt_decoded: Dict = jose_jwt.decode(
        token=sender_jwt, options=decode_options, key=None
    )
    receiver_jwt_decoded: Dict = jose_jwt.decode(
        token=receiver_jwt, options=decode_options, key=None
    )
    context.clinician_uuid = sender_jwt_decoded["metadata"]["clinician_id"]
    context.patient_uuid = receiver_jwt_decoded["metadata"]["patient_id"]

    chunk = []
    letters = string.ascii_letters
    for i in range(number_messages):
        message_details: Dict = {
            "message_type": {"value": message_helper.MessageTypes.GENERAL.value},
            "sender_type": "clinician",
            "sender": sender_jwt_decoded["metadata"]["clinician_id"],
            "receiver_type": "patient",
            "receiver": receiver_jwt_decoded["metadata"]["patient_id"],
            "content": "".join(
                letters for _ in range(random.randint(128 // 2, 128 * 2))
            ),
        }
        chunk.append(message_details)

        if len(chunk) == 500 or i == number_messages - 1:
            response = messages_client.send_messages(
                jwt=context.system_jwt, messages_list=chunk
            )
            assert response.status_code == 201, response.status_code
            chunk.clear()


@when("timing this step")
def timing_step(context: Context) -> None:
    context.start_time = time.time()


@step("the clinician gets messages by {unique_uuid_belongs_to} uuid")
def retrieve_messages(context: Context, unique_uuid_belongs_to: str) -> None:
    uuid = (
        context.patient_uuid
        if unique_uuid_belongs_to == "patient"
        else context.clinician_uuid
    )
    context.messages = messages_client.get_messages_by_sender_or_receiver(
        jwt=context.clinician_jwt, uuid=uuid
    ).json()


@then("it takes less than {seconds} seconds to return a list of messages")
def takes_less_than(context: Context, seconds: str) -> None:
    limit = float(seconds)
    end_time = time.time()
    diff = end_time - context.start_time
    assert (
        diff < limit
    ), f"Max time for the test exceeded {limit} seconds - it took {diff} seconds"


@step("all the messages are retrieved")
def check_messages(context: Context) -> None:
    assert (
        len(context.messages) == context.number_messages
    ), f"Retrieved {len(context.messages)} messages instead of {context.number_messages}: {context.messages}"
