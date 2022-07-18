import json
from datetime import datetime
from typing import Any, Dict, Generator, List, Tuple

import pytest
from flask import Flask, g
from flask_batteries_included.sqldb import db
from pytest_dhos.jwt_permissions import GDM_CLINICIAN_PERMISSIONS
from sqlalchemy.exc import SQLAlchemyError

from dhos_messages_api.blueprint_api import controller
from dhos_messages_api.models.message import Message
from dhos_messages_api.models.message_type import MessageType

GDM_PATIENT_PERMISSIONS = [
    "read:gdm_patient_abbreviated",
    "read:gdm_message",
    "write:gdm_message",
    "read:gdm_bg_reading",
    "write:gdm_bg_reading",
    "read:gdm_medication",
    "read:gdm_question",
    "read:gdm_answer",
    "write:gdm_answer",
    "read:gdm_telemetry",
    "write:gdm_telemetry",
    "write:gdm_terms_agreement",
]


@pytest.fixture
def app(mocker: Any) -> Flask:
    """Fixture that creates app for testing"""
    from flask_batteries_included.helpers.security import _ProtectedRoute

    import dhos_messages_api.app

    app: Flask = dhos_messages_api.app.create_app(
        testing=True, use_pgsql=False, use_sqlite=True
    )

    def mock_claims(self: Any, verify: bool = True) -> Tuple:
        return getattr(g, "jwt_claims", {}), getattr(g, "jwt_scopes", [])

    mocker.patch.object(_ProtectedRoute, "_retrieve_jwt_claims", mock_claims)
    app.config["IGNORE_JWT_VALIDATION"] = False

    return app


@pytest.fixture
def app_context(app: Flask) -> Generator[None, None, None]:
    with app.app_context():
        yield


@pytest.fixture
def jwt_valid_patient() -> Dict:
    return {"patient_id": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161"}


@pytest.fixture
def jwt_gdm_patient_uuid(app_context: Any, jwt_scopes: Any) -> str:
    """Use this fixture to make requests as a GDM patient"""
    from flask import g

    gdm_patient = "5c4f1d24-2952-4d4e-b1d1-3637e33cc161"
    g.jwt_claims = {"patient_id": gdm_patient}
    if jwt_scopes is None:
        g.jwt_scopes = GDM_PATIENT_PERMISSIONS
    else:
        if isinstance(jwt_scopes, str):
            jwt_scopes = jwt_scopes.split(",")
        g.jwt_scopes = jwt_scopes
    return gdm_patient


@pytest.fixture
def jwt_gdm_clinician_uuid(app_context: Any, jwt_scopes: Any) -> str:
    """Use this fixture to make requests as a GDM clinician"""
    from flask import g

    gdm_clinician = "4c4f1d24-2952-4d4e-b1d1-3637e33cc161"
    g.jwt_claims = {
        "clinician_id": gdm_clinician,
        "location_ids": ["1"],
    }
    if jwt_scopes is None:
        g.jwt_scopes = GDM_CLINICIAN_PERMISSIONS
    else:
        if isinstance(jwt_scopes, str):
            jwt_scopes = jwt_scopes.split(",")
        g.jwt_scopes = jwt_scopes
    return gdm_clinician


@pytest.fixture
def jwt_gdm_another_clinician_uuid(app_context: Any, jwt_scopes: Any) -> str:
    """Use this fixture to make requests as a different GDM clinician"""
    from flask import g

    gdm_clinician = "999f1d24-2952-4d4e-b1d1-3637e33cc161"
    g.jwt_claims = {
        "clinician_id": gdm_clinician,
        "location_ids": ["21"],
    }
    if jwt_scopes is None:
        g.jwt_scopes = GDM_CLINICIAN_PERMISSIONS
    else:
        if isinstance(jwt_scopes, str):
            jwt_scopes = jwt_scopes.split(",")
        g.jwt_scopes = jwt_scopes
    return gdm_clinician


@pytest.fixture
def jwt_valid_clinician() -> Dict:
    return {
        "clinician_id": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "location_ids": ["1"],
    }


@pytest.fixture
def jwt_invalid_clinician() -> Dict:
    return {
        "clinician_id": "999f1d24-2952-4d4e-b1d1-3637e33cc161",
        "location_ids": ["21"],
    }


@pytest.fixture()
def message_types() -> Generator[List[Message], None, None]:
    message_types = [
        MessageType(
            uuid="DHOS-MESSAGES-GENERAL",
            created=datetime.utcnow(),
            modified=datetime.utcnow(),
            value=0,
        ),
        MessageType(
            uuid="DHOS-MESSAGES-DOSAGE",
            created=datetime.utcnow(),
            modified=datetime.utcnow(),
            value=1,
        ),
        MessageType(
            uuid="DHOS-MESSAGES-DIETARY",
            created=datetime.utcnow(),
            modified=datetime.utcnow(),
            value=2,
        ),
        MessageType(
            uuid="DHOS-MESSAGES-FEEDBACK",
            created=datetime.utcnow(),
            modified=datetime.utcnow(),
            value=3,
        ),
        MessageType(
            uuid="DHOS-MESSAGES-CALLBACK",
            created=datetime.utcnow(),
            modified=datetime.utcnow(),
            value=5,
        ),
        MessageType(
            uuid="DHOS-MESSAGES-ACTIVATION-CODE",
            created=datetime.utcnow(),
            modified=datetime.utcnow(),
            value=6,
        ),
        MessageType(
            uuid="DHOS-MESSAGES-RED-ALERT",
            created=datetime.utcnow(),
            modified=datetime.utcnow(),
            value=7,
        ),
        MessageType(
            uuid="DHOS-MESSAGES-AMBER-ALERT",
            created=datetime.utcnow(),
            modified=datetime.utcnow(),
            value=8,
        ),
    ]

    db.session.add_all(message_types)
    db.session.commit()

    yield message_types

    for m in message_types:
        try:
            db.session.delete(m)
        except SQLAlchemyError:
            pass
    db.session.commit()


@pytest.fixture
def message_dict_good() -> Dict:
    return {
        "sender": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "sender_type": "patient",
        "receiver": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "receiver_type": "clinician",
        "message_type": {"value": 1},
        "content": "I've eaten cake :(",
    }


@pytest.fixture
def message_good(message_dict_good: Dict) -> Dict:
    return controller.create_message(message_details=message_dict_good)


@pytest.fixture
def message_dict_alert() -> Dict:
    return {
        "sender": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "sender_type": "patient",
        "receiver": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "receiver_type": "location",
        "message_type": {"value": 7},
        "content": "RED ALERT",
    }


@pytest.fixture
def message_alert(message_dict_alert: Dict) -> Dict:
    return controller.create_message(message_details=message_dict_alert)


@pytest.fixture
def message_dict_location_one() -> Dict:
    return {
        "sender": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "sender_type": "patient",
        "receiver": "1",
        "receiver_type": "location",
        "message_type": {"value": 1},
        "content": "I've eaten cake :(",
    }


@pytest.fixture
def message_location_one(message_dict_location_one: Dict) -> Dict:
    return controller.create_message(message_details=message_dict_location_one)


@pytest.fixture
def message_dict_clinician_good() -> Dict:
    return {
        "sender": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "sender_type": "clinician",
        "receiver": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "receiver_type": "patient",
        "message_type": {"value": 1},
        "content": "I love cake too, but enough is enough please restrain yourself",
    }


@pytest.fixture
def message_good_clinician_to_patient(message_dict_clinician_good: Dict) -> Dict:
    return controller.create_message(message_details=message_dict_clinician_good)


@pytest.fixture
def message_dict_bad() -> Dict:
    return {
        "sender": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "sender_type": "clinician",
        "receiver": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "receiver_type": "patient",
        "message_type": {"value": 1},
        "content": "I love cake too, but enough is enough please restrain yourself",
        "rubbish": "104f1d24-2952-4d4e-b1d1-3637e33cc161",
    }


@pytest.fixture
def message_dict_zero_len_field() -> Dict:
    return {
        "sender": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "sender_type": "clinician",
        "receiver": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "receiver_type": "patient",
        "message_type": {"value": 1},
        "content": "I love cake too, but enough is enough please restrain yourself",
        "retrieved": "",
    }


@pytest.fixture
def message_dict_null_field() -> Dict:
    return {
        "sender": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "sender_type": "clinician",
        "receiver": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "receiver_type": "patient",
        "message_type": {"value": 1},
        "content": "I love cake too, but enough is enough please restrain yourself",
        "retrieved": None,
    }


@pytest.fixture
def message_dict_empty_required() -> Dict:
    return {
        "sender": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "sender_type": "clinician",
        "receiver": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "receiver_type": "patient",
        "message_type": "",
        "content": "I love cake too, but enough is enough please restrain yourself",
    }


@pytest.fixture
def message_dict_invalid_related() -> Dict:
    return {
        "sender": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "sender_type": "clinician",
        "receiver": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "receiver_type": "patient",
        "message_type": {"value": 1},
        "content": "I love cake too, but enough is enough please restrain yourself",
        "related_message": "104f1d24-2952-4d4e-b1d1-3637e33cc161",
    }


@pytest.fixture
def message_dict_invalid_message_type() -> Dict:
    return {
        "sender": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "sender_type": "clinician",
        "receiver": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "receiver_type": "patient",
        "message_type": {"value": 9},
        "content": "I love cake too, but enough is enough please restrain yourself",
    }


@pytest.fixture
def message_dict_callback() -> Dict:
    return {
        "sender": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "sender_type": "clinician",
        "receiver": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "receiver_type": "location",
        "message_type": {"value": 5},
        "content": "call me",
    }


@pytest.fixture
def message_callback(message_dict_callback: Dict) -> Dict:
    return controller.create_message(message_details=message_dict_callback)


@pytest.fixture
def message_dict_deprecated_callback() -> Dict:
    return {
        "sender": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "sender_type": "clinician",
        "receiver": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        "receiver_type": "location",
        "message_type": {"value": 4},
        "content": "call me",
    }


@pytest.fixture()
def mock_bearer_validation(mocker: Any) -> Any:
    from jose import jwt

    mocked = mocker.patch.object(jwt, "get_unverified_claims")
    mocked.return_value = {
        "sub": "1234567890",
        "name": "John Doe",
        "iat": 1_516_239_022,
        "iss": "http://localhost/",
    }
    return mocked
