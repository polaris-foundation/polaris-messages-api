from typing import Any, Dict, List, Optional, Tuple

import connexion
from flask import request
from she_logging import logger

from dhos_messages_api.models.message import Message


def get_clinician_locations() -> List[str]:
    filter_ids: List[str] = request.headers.get("X-Location-Ids", "").split(",")
    logger.debug("Clinician locations %s", filter_ids)
    return filter_ids


def user_type_to_validate(user_id: str, jwt_claims: Optional[Dict]) -> Optional[str]:
    if jwt_claims is None:
        return None
    if jwt_claims.get("patient_id"):
        return "patient"
    if jwt_claims.get("clinician_id"):
        if user_id == jwt_claims["clinician_id"]:
            return "clinician"
        elif user_id in get_clinician_locations():
            return "location"

    return None


def get_ids_to_validate(jwt_claims: Dict) -> Tuple[List[str], List[str]]:
    user_types = []
    ids_to_validate = []
    if jwt_claims.get("patient_id"):
        ids_to_validate = [jwt_claims["patient_id"]]
        user_types.append("patient")
    if jwt_claims.get("clinician_id"):
        ids_to_validate.append(jwt_claims["clinician_id"])
        user_types.append("clinician")
        location_ids = get_clinician_locations()
        if location_ids:
            ids_to_validate.extend(location_ids)
            user_types.append("location")
    if jwt_claims.get("system_id"):
        ids_to_validate.append(jwt_claims["system_id"])
        user_types.append("system")

    return ids_to_validate, user_types


def create_message_protection(
    jwt_claims: Dict, claims_map: Optional[Dict], **params: Any
) -> bool:
    # Patient can only create to a location
    request_data = connexion.request.get_json()
    return create_message_protection_base(jwt_claims, request_data)


def create_message_protection_base(jwt_claims: Dict, request_data: Dict) -> bool:
    # message worker service can create messages on behalf of users
    if jwt_claims.get("system_id") == "dhos-messages-adapter-worker":
        return True

    if "patient_id" in jwt_claims:
        if (
            request_data["receiver_type"] != "location"
            or request_data["sender"] != jwt_claims["patient_id"]
        ):
            return False
    else:
        # Clinician/location need to have a sender from their JWT
        ids_to_validate, user_types = get_ids_to_validate(jwt_claims)
        if request_data["sender"] not in ids_to_validate:
            return False

    return True


def message_by_id_protection(
    jwt_claims: Dict, claims_map: Optional[Dict], **params: Any
) -> bool:
    ids_to_validate, user_types = get_ids_to_validate(jwt_claims)

    message = Message.query.filter_by(uuid=params["message_id"]).first_or_404()

    for id_to_validate in ids_to_validate:
        if (message.sender == id_to_validate and message.sender_type in user_types) or (
            message.receiver == id_to_validate and message.receiver_type in user_types
        ):
            return True

    return False


def sender_receiver_protection(
    jwt_claims: Dict, claims_map: Optional[Dict], **params: Any
) -> bool:
    ids = ["receiver_id", "sender_id"]
    return ids_match(ids, jwt_claims, claims_map, **params)


def sender_or_receiver_protection(
    jwt_claims: Dict, claims_map: Optional[Dict], **params: Any
) -> bool:
    if jwt_claims is None:
        return False

    if jwt_claims.get("clinician_id"):
        return True

    ids = ["unique_id"]
    return ids_match(ids, jwt_claims, claims_map, **params)


def ids_match(
    ids: List[str], jwt_claims: Dict, claims_map: Optional[Dict], **params: Any
) -> bool:
    ids_to_validate, user_types = get_ids_to_validate(jwt_claims)

    # The dhos-aggregator-api system can log in and view messages
    if user_types == ["system"] and ids_to_validate == ["dhos-aggregator-api"]:
        return True

    for named_param in ids:
        if params.get(named_param):
            if params[named_param] in ids_to_validate:
                return True

    # No one else can get in
    return False
