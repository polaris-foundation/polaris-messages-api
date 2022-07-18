from typing import Any, Dict, List

import requests
from environs import Env
from requests import Response


def _get_base_url() -> str:
    base_url: str = Env().str("DHOS_MESSAGES_BASE_URL", "http://dhos-messages-api:5000")
    return base_url


def reset_db(jwt: str) -> Response:
    return requests.post(
        f"{_get_base_url()}/drop_data",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
    )


def send_messages(jwt: str, messages_list: List[Dict]) -> Response:
    return requests.post(
        f"{_get_base_url()}/create_messages",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
        json=messages_list,
    )


def send_message(jwt: str, body: Dict, headers: Dict = None) -> Response:
    if headers is None:
        headers = {}
    return requests.post(
        f"{_get_base_url()}/dhos/v1/message",
        timeout=15,
        headers={**headers, "Authorization": f"Bearer {jwt}"},
        json=body,
    )


def send_message_v2(jwt: str, body: Dict, headers: Dict = None) -> Response:
    if headers is None:
        headers = {}
    return requests.post(
        f"{_get_base_url()}/dhos/v2/message",
        timeout=15,
        headers={**headers, "Authorization": f"Bearer {jwt}"},
        json=body,
    )


def update_message(jwt: str, uuid: str, body: Dict) -> Response:
    return requests.patch(
        f"{_get_base_url()}/dhos/v1/message/{uuid}",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
        json=body,
    )


def get_all_messages(jwt: str) -> Response:
    return requests.get(
        f"{_get_base_url()}/dhos/v1/message",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
    )


def get_messages_by_sender(jwt: str, uuid: str, **kwargs: Any) -> Response:
    return _do_get_messages_by_endpoint(jwt=jwt, uuid=uuid, endpoint="sender")


def get_messages_by_receiver(jwt: str, uuid: str, **kwargs: Any) -> Response:
    return _do_get_messages_by_endpoint(jwt=jwt, uuid=uuid, endpoint="receiver")


def get_active_messages_by_sender(jwt: str, uuid: str, **kwargs: Any) -> Response:
    return _do_get_active_messages_by_endpoint(jwt=jwt, uuid=uuid, endpoint="sender")


def get_active_messages_by_receiver(jwt: str, uuid: str, **kwargs: Any) -> Response:
    return _do_get_active_messages_by_endpoint(jwt=jwt, uuid=uuid, endpoint="receiver")


def get_messages_by_sender_and_receiver(
    jwt: str, sender_uuid: str, receiver_uuid: str, **kwargs: Any
) -> Response:
    return requests.get(
        f"{_get_base_url()}/dhos/v1/sender/{sender_uuid}/receiver/{receiver_uuid}/message",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
    )


def get_messages_by_sender_or_receiver(jwt: str, uuid: str, **kwargs: Any) -> Response:
    return requests.get(
        f"{_get_base_url()}/dhos/v1/sender_or_receiver/{uuid}/message",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
    )


def retrieve_active_callbacks_for_list_of_patients(
    jwt: str, patient_uuids: List[str], **kwargs: Any
) -> Response:
    return requests.post(
        f"{_get_base_url()}/dhos/v1/active/callback/message",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
        json=patient_uuids,
    )


def delete_message(jwt: str, uuid: str) -> Response:
    return requests.delete(
        f"{_get_base_url()}/dhos/v1/message/{uuid}",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
    )


def _do_get_messages_by_endpoint(
    jwt: str, uuid: str, endpoint: str, **kwargs: Any
) -> Response:
    return requests.get(
        f"{_get_base_url()}/dhos/v1/{endpoint}/{uuid}/message",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
    )


def _do_get_active_messages_by_endpoint(
    jwt: str, uuid: str, endpoint: str, **kwargs: Any
) -> Response:
    return requests.get(
        f"{_get_base_url()}/dhos/v1/{endpoint}/{uuid}/active/message",
        timeout=15,
        headers={"Authorization": f"Bearer {jwt}"},
    )
