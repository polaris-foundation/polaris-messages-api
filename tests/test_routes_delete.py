from typing import Dict

import pytest
from flask.testing import FlaskClient


@pytest.mark.usefixtures("message_types", "app", "mock_bearer_validation")
class TestDelete:
    def test_delete_message_deprecated(
        self,
        client: FlaskClient,
        message_good: Dict,
        jwt_gdm_patient_uuid: str,
    ) -> None:
        response = client.delete(
            f'/dhos/v1/message/{message_good["uuid"]}',
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 405
