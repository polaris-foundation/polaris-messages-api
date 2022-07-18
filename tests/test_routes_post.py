from typing import Dict

import pytest
from flask.testing import FlaskClient


@pytest.mark.usefixtures("message_types", "app", "mock_bearer_validation")
class TestPost:
    def test_post_message(
        self,
        client: FlaskClient,
        message_dict_good: Dict,
        jwt_system: str,
    ) -> None:
        response = client.post(
            "/dhos/v1/message",
            json=message_dict_good,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    def test_post_message_clinician(
        self,
        client: FlaskClient,
        message_dict_clinician_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.post(
            "/dhos/v1/message",
            json=message_dict_clinician_good,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json["content"] == message_dict_clinician_good["content"]

    def test_post_message_bad_data(
        self,
        client: FlaskClient,
        message_dict_bad: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.post(
            "/dhos/v1/message",
            json=message_dict_bad,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_post_message_zero_len_field(
        self,
        client: FlaskClient,
        message_dict_zero_len_field: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.post(
            "/dhos/v1/message",
            json=message_dict_zero_len_field,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_post_message_empty_data(
        self,
        client: FlaskClient,
        message_dict_empty_required: Dict,
    ) -> None:
        response = client.post(
            "/dhos/v1/message",
            json=message_dict_empty_required,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_post_message_invalid_related(
        self,
        client: FlaskClient,
        message_dict_invalid_related: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.post(
            "/dhos/v1/message",
            json=message_dict_invalid_related,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_post_message_invalid_message_type(
        self,
        client: FlaskClient,
        message_dict_invalid_message_type: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.post(
            "/dhos/v1/message",
            json=message_dict_invalid_message_type,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_callback_request(
        self,
        client: FlaskClient,
        message_dict_callback: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.post(
            "/dhos/v1/message",
            json=message_dict_callback,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    def test_deprecated_callback_request(
        self,
        client: FlaskClient,
        message_dict_deprecated_callback: Dict,
    ) -> None:
        response = client.post(
            "/dhos/v1/message",
            json=message_dict_deprecated_callback,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_get_active_callback_messages_for_patients(
        self,
        client: FlaskClient,
        message_callback: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.post(
            "/dhos/v1/active/callback/message",
            json=["4c4f1d24-2952-4d4e-b1d1-3637e33cc161"],
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert (
            response.json[message_callback["sender"]]["uuid"]
            == message_callback["uuid"]
        )

    def test_post_message_v2_clinician(
        self,
        client: FlaskClient,
        message_dict_clinician_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.post(
            "/dhos/v2/message",
            json=message_dict_clinician_good,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json["content"] == message_dict_clinician_good["content"]

    def test_post_message_v2_empty_400(
        self,
        client: FlaskClient,
        message_dict_empty_required: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.post(
            "/dhos/v2/message",
            json=message_dict_empty_required,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400
