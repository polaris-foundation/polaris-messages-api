import json
from typing import Any, Dict, Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from dhos_messages_api.helper.security import (
    create_message_protection_base,
    message_by_id_protection,
    sender_or_receiver_protection,
    sender_receiver_protection,
    user_type_to_validate,
)


@pytest.fixture
def dummy_location_ids(app: Flask) -> Generator[None, None, None]:
    with app.test_request_context(headers={"X-Location-Ids": "1,2"}):
        yield


@pytest.mark.usefixtures("message_types", "app")
class TestSecurity:
    def test_create_message_protection_system_id_good(self) -> None:
        jwt_claims = {"system_id": "dhos-messages-adapter-worker"}
        request_data = {
            "sender": "3",
            "sender_type": "patient",
            "receiver": "5",
            "receiver_type": "location",
            "message_type": {"value": 1},
            "content": "I love cake :(",
        }
        assert create_message_protection_base(jwt_claims, request_data) is True

    def test_create_message_protection_system_id_bad(self) -> None:
        jwt_claims = {"system_id": "another-system"}
        request_data = {
            "sender": "3",
            "sender_type": "patient",
            "receiver": "5",
            "receiver_type": "location",
            "message_type": {"value": 1},
            "content": "I love cake :(",
        }
        assert create_message_protection_base(jwt_claims, request_data) is False

    def test_create_message_protection_base_patient_good(self) -> None:
        jwt_claims = {"patient_id": "1"}
        request_data = {
            "sender": "1",
            "sender_type": "patient",
            "receiver": "4",
            "receiver_type": "location",
            "message_type": {"value": 1},
            "content": "I love cake :(",
        }
        assert create_message_protection_base(jwt_claims, request_data) is True

    def test_create_message_protection_base_patient_bad(self) -> None:
        jwt_claims = {"patient_id": "1"}
        request_data = {
            "sender": "3",
            "sender_type": "patient",
            "receiver": "4",
            "receiver_type": "location",
            "message_type": {"value": 1},
            "content": "I love cake :(",
        }
        assert create_message_protection_base(jwt_claims, request_data) is False

    def test_create_message_protection_base_clinician_good(
        self, dummy_location_ids: None
    ) -> None:
        jwt_claims = {"clinician_id": "1"}
        request_data = {
            "sender": "1",
            "sender_type": "clinician",
            "receiver": "4",
            "receiver_type": "location",
            "message_type": {"value": 1},
            "content": "I love cake :(",
        }
        assert create_message_protection_base(jwt_claims, request_data) is True

    def test_create_message_protection_base_clinician_bad(self) -> None:
        jwt_claims = {"clinician_id": "10"}
        request_data = {
            "sender": "1",
            "sender_type": "clinician",
            "receiver": "4",
            "receiver_type": "location",
            "message_type": {"value": 1},
            "content": "I love cake :(",
        }
        assert create_message_protection_base(jwt_claims, request_data) is False

    def test_message_by_id_protection_good_patient(self, message_good: Dict) -> None:
        jwt_claims = {"patient_id": "5c4f1d24-2952-4d4e-b1d1-3637e33cc161"}
        assert (
            message_by_id_protection(jwt_claims, None, message_id=message_good["uuid"])
            is True
        )

    def test_message_by_id_protection_bad_patient(self, message_good: Dict) -> None:
        jwt_claims = {"patient_id": "7"}
        assert (
            message_by_id_protection(jwt_claims, None, message_id=message_good["uuid"])
            is False
        )

    def test_message_by_id_protection_good_clinician(
        self, message_good: Dict, dummy_location_ids: None
    ) -> None:
        jwt_claims = {
            "clinician_id": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        }
        assert (
            message_by_id_protection(jwt_claims, None, message_id=message_good["uuid"])
            is True
        )

    def test_message_by_id_protection_bad_clinician(
        self, message_good: Dict, dummy_location_ids: None
    ) -> None:
        jwt_claims = {"clinician_id": "15"}
        assert (
            message_by_id_protection(jwt_claims, None, message_id=message_good["uuid"])
            is False
        )

    def test_sender_receiver_protection_good(self, dummy_location_ids: None) -> None:
        jwt_claims: Dict = {
            "clinician_id": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        }
        assert (
            sender_receiver_protection(
                jwt_claims, None, receiver_id="4c4f1d24-2952-4d4e-b1d1-3637e33cc161"
            )
            is True
        )

        jwt_claims = {
            "patient_id": "274183fb-919e-4bc4-8224-8d4e1b212496",
            "exp": 1525097309,
        }

        assert (
            sender_receiver_protection(
                jwt_claims, None, sender_id="274183fb-919e-4bc4-8224-8d4e1b212496"
            )
            is True
        )

    def test_sender_or_receiver_protection(self, dummy_location_ids: None) -> None:
        jwt_claims: Dict = {
            "clinician_id": "4c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        }
        assert (
            sender_or_receiver_protection(
                jwt_claims, None, receiver_id="4c4f1d24-2952-4d4e-b1d1-3637e33cc161"
            )
            is True
        )

        jwt_claims = {
            "patient_id": "274183fb-919e-4bc4-8224-8d4e1b212496",
            "exp": 1525097309,
        }

        assert (
            sender_or_receiver_protection(
                jwt_claims, None, sender_id="274183fb-919e-4bc4-8224-8d4e1b212496"
            )
            is False
        )

        assert (
            sender_or_receiver_protection(
                jwt_claims, None, unique_id="274183fb-919e-4bc4-8224-8d4e1b212496"
            )
            is True
        )

    def test_sender_receiver_protection_bad(self, dummy_location_ids: None) -> None:
        jwt_claims = {"clinician_id": "11111111"}
        assert (
            sender_receiver_protection(
                jwt_claims, None, receiver_id="4c4f1d24-2952-4d4e-b1d1-3637e33cc161"
            )
            is False
        )

    def test_user_type_to_validate_patient(self) -> None:
        jwt_claims = {"patient_id": "7"}
        assert user_type_to_validate("7", jwt_claims) == "patient"

    def test_user_type_to_validate_clinician(self) -> None:
        jwt_claims = {"clinician_id": "7"}
        assert user_type_to_validate("7", jwt_claims) == "clinician"

    def test_user_type_to_validate_location(self, dummy_location_ids: None) -> None:
        jwt_claims = {"clinician_id": "11111111"}
        assert user_type_to_validate("1", jwt_claims) == "location"

    def test_user_type_to_validate_location_bad(self, dummy_location_ids: None) -> None:
        jwt_claims = {"clinician_id": "11111111"}
        assert user_type_to_validate("3", jwt_claims) is None
