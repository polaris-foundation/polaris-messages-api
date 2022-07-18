from typing import Any, Dict

import pytest
from flask.testing import FlaskClient


@pytest.mark.usefixtures("message_types", "app", "mock_bearer_validation")
class TestGet:
    def test_get_all_messages_endpoint_deprecated(self, client: FlaskClient) -> None:
        response = client.get("/dhos/v1/message")
        assert response.status_code == 405

    def test_get_message_response_includes_identifier(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_patient_uuid: str,
    ) -> None:
        response = client.get(
            f"/dhos/v1/message/{message_good['uuid']}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.json is not None
        for field in ["uuid", "created", "created_by", "modified", "modified_by"]:
            assert field in response.json

    def test_get_message_patient(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_patient_uuid: str,
    ) -> None:

        response = client.get(
            f"/dhos/v1/message/{message_good['uuid']}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    def test_get_message_clinician(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.get(
            f"/dhos/v1/message/{message_good['uuid']}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    def test_get_messages_by_sender(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_patient_uuid: str,
    ) -> None:
        response = client.get(
            f"/dhos/v1/sender/{message_good['sender']}/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    def test_get_active_messages_by_sender(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_patient_uuid: str,
    ) -> None:
        response = client.get(
            f"/dhos/v1/sender/{message_good['sender']}/active/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    def test_get_messages_by_receiver(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.get(
            f"/dhos/v1/receiver/{message_good['receiver']}/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    def test_get_messages_by_sender_or_receiver(
        self,
        client: FlaskClient,
        jwt_gdm_patient_uuid: str,
        message_good: Dict,
    ) -> None:
        # Given a good message from a patient to a clinician
        # When the patient requests their messages
        response = client.get(
            f"/dhos/v1/sender_or_receiver/{message_good['sender']}/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        # Then they get the message
        assert response.status_code == 200
        assert response.json is not None
        assert_messages_equal(response.json[0], message_good)

    def test_get_messages_by_sender_or_receiver_patient_not_view_alerts(
        self,
        client: FlaskClient,
        jwt_gdm_patient_uuid: str,
        message_alert: Dict,
    ) -> None:
        response = client.get(
            f"/dhos/v1/sender_or_receiver/{message_alert['sender']}/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json == []

    def test_get_messages_by_sender_or_receiver_valid_clinician(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        # Given a good message from a patient to a clinician
        # When the clinician requests the patient's messages
        response = client.get(
            f"/dhos/v1/sender_or_receiver/{message_good['sender']}/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        # Then they get the message
        assert response.status_code == 200
        assert response.json is not None
        assert_messages_equal(response.json[0], message_good)

    def test_get_messages_by_sender_or_receiver_another_clinician(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_another_clinician_uuid: str,
    ) -> None:
        # Given a good message from a patient to a clinician
        # When _another_ clinician requests the patient's messages
        response = client.get(
            f"/dhos/v1/sender_or_receiver/{message_good['sender']}/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        # Then they get the message
        assert response.status_code == 200
        assert response.json is not None
        assert_messages_equal(response.json[0], message_good)

    def test_get_messages_by_sender_or_receiver_invalid_clinician(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_another_clinician_uuid: str,
    ) -> None:
        # Given a good message from a patient to a clinician
        # When _another_ clinician requests the clinician's messages
        response = client.get(
            f"/dhos/v1/sender_or_receiver/{message_good['receiver']}/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        # They don't get the message
        assert response.status_code == 200
        assert response.json is not None
        assert response.json == []

    def test_get_messages_by_sender_or_receiver_location(
        self,
        client: FlaskClient,
        message_location_one: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.get(
            f"/dhos/v1/sender_or_receiver/{message_location_one['sender']}/message",
            headers={"Authorization": "Bearer TOKEN", "X-Location-Ids": "1,2"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json[0]["receiver"] == message_location_one["receiver"]

    def test_get_messages_by_sender_or_receiver_c_to_p(
        self,
        client: FlaskClient,
        message_good_clinician_to_patient: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        # Given a good message from a clinician to a patient

        # When the clinician requests the patient's messages
        response = client.get(
            f"/dhos/v1/sender_or_receiver/{message_good_clinician_to_patient['receiver']}/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        # Then they get the message
        assert response.status_code == 200
        assert response.json is not None
        assert_messages_equal(response.json[0], message_good_clinician_to_patient)

    def test_get_messages_by_sender_or_receiver_c_to_p_another_clinician(
        self,
        client: FlaskClient,
        message_good_clinician_to_patient: Dict,
        jwt_gdm_another_clinician_uuid: str,
    ) -> None:
        # Given a good message from a clinician to a patient
        # When _another_ clinician requests the patient's messages
        response = client.get(
            f"/dhos/v1/sender_or_receiver/{message_good_clinician_to_patient['receiver']}/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        # Then they get the message
        assert response.status_code == 200
        assert response.json is not None
        assert_messages_equal(response.json[0], message_good_clinician_to_patient)

    def test_get_messages_by_sender_and_receiver(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_patient_uuid: str,
    ) -> None:
        response = client.get(
            f"/dhos/v1/sender/{message_good['sender']}/receiver/{message_good['receiver']}/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    def test_get_active_messages_by_sender_and_receiver(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_patient_uuid: str,
    ) -> None:
        response = client.get(
            f"/dhos/v1/sender/{message_good['sender']}/receiver/{message_good['receiver']}/active/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    def test_get_active_callback_messages_by_receiver(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.get(
            f"/dhos/v1/receiver/{message_good['receiver']}/active/callback/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    def test_get_active_messages_by_receiver(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.get(
            f"/dhos/v1/receiver/{message_good['receiver']}/active/message",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200


def assert_messages_equal(a: Dict, b: Dict) -> None:
    fields_to_ignore = {
        "created": "",
        "modified": "",
        "message_type": "",
    }
    a_to_compare = {**a, **fields_to_ignore}
    b_to_compare = {**b, **fields_to_ignore}
    assert a["message_type"]["value"] == b["message_type"]["value"]
    assert a_to_compare == b_to_compare
