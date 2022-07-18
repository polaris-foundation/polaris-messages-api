from typing import Dict

import pytest
from flask.testing import FlaskClient


@pytest.mark.usefixtures("message_types", "app", "mock_bearer_validation")
class TestPatch:
    valid_updates = [
        {"retrieved": "2018-02-11T11:59:50.123+03:00"},
        {"confirmed": "2018-02-11T11:59:50.123+03:00"},
        {"cancelled": "2018-02-11T11:59:50.123+03:00"},
        {"confirmed_by": "ac8459b0-6a9a-4e8e-a2de-41c5dd9b81aa"},
        {"cancelled_by": "ac8459b0-6a9a-4e8e-a2de-41c5dd9b81aa"},
        # related_message needs to be a real message - handled in its own test
    ]

    invalid_updates = [
        {"sender": "ac8459b0-6a9a-4e8e-a2de-41c5dd9b81aa"},
        {"sender_type": "clinician"},
        {"receiver": "ac8459b0-6a9a-4e8e-a2de-41c5dd9b81aa"},
        {"receiver_type": "patient"},
        {"message_type": {"value": 1}},
        {"content": "shouldn't be updated"},
    ]

    def test_update_message(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        confirmed_by = "ac8459b0-6a9a-4e8e-a2de-41c5dd9b81aa"
        update = {"confirmed_by": confirmed_by}
        response = client.patch(
            f"/dhos/v1/message/{message_good['uuid']}",
            json=update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json["confirmed_by"] == confirmed_by

    def test_update_message_retrieved(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        retrieved_date = "2018-02-11T11:59:50.123+03:00"
        update = {"retrieved": retrieved_date}
        response = client.patch(
            f"/dhos/v1/message/{message_good['uuid']}",
            json=update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.json is not None
        assert response.json["retrieved"] == retrieved_date

    def test_update_message_cancelled(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        cancelled = "2018-02-11T11:59:50.123+03:00"
        cancelled_by = "1234"
        update = {"cancelled": cancelled, "cancelled_by": cancelled_by}
        response = client.patch(
            f"/dhos/v1/message/{message_good['uuid']}",
            json=update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.json is not None
        assert response.json["cancelled"] == cancelled
        assert response.json["cancelled_by"] == cancelled_by

    def test_update_message_bad(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        update = {"rubbish": "ac8459b0-6a9a-4e8e-a2de-41c5dd9b81aa"}
        response = client.patch(
            f"/dhos/v1/message/{message_good['uuid']}",
            json=update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_update_empty_message(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        update: Dict = {}
        response = client.patch(
            f"/dhos/v1/message/{message_good['uuid']}",
            json=update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_update_comment_message(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        update = {"content": "you shouldnt change"}
        response = client.patch(
            f"/dhos/v1/message/{message_good['uuid']}",
            json=update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_update_related_message(
        self,
        client: FlaskClient,
        message_good: Dict,
        message_alert: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        update = {"related_message": message_alert["uuid"]}
        response = client.patch(
            f"/dhos/v1/message/{message_good['uuid']}",
            json=update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json["related_message"] == message_alert["uuid"]

    def test_update_circular_related_message(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        update = {"related_message": message_good["uuid"]}
        response = client.patch(
            f"/dhos/v1/message/{message_good['uuid']}",
            json=update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_update_zero_length_optional(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        update = {"retrieved": ""}
        response = client.patch(
            f"/dhos/v1/message/{message_good['uuid']}",
            json=update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_update_null_optional(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        update = {"retrieved": None}
        response = client.patch(
            f"/dhos/v1/message/{message_good['uuid']}",
            json=update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    @pytest.mark.parametrize("update", valid_updates, ids=lambda u: str(u.keys()))
    def test_update_updatable_fields(
        self,
        client: FlaskClient,
        message_good: Dict,
        update: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.patch(
            f"/dhos/v1/message/{message_good['uuid']}",
            json=update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

    @pytest.mark.parametrize("update", invalid_updates, ids=lambda u: str(u.keys()))
    def test_update_non_updatable_fields_fails(
        self,
        client: FlaskClient,
        message_good: Dict,
        update: Dict,
        jwt_gdm_clinician_uuid: str,
    ) -> None:
        response = client.patch(
            f"/dhos/v1/message/{message_good['uuid']}",
            json=update,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400
