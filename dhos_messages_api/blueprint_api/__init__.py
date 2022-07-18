import connexion
import flask
from flask import Response
from flask_batteries_included.helpers.routes import deprecated_route
from flask_batteries_included.helpers.security import protected_route
from flask_batteries_included.helpers.security.endpoint_security import (
    and_,
    or_,
    scopes_present,
)
from marshmallow import RAISE

from dhos_messages_api.blueprint_api import controller
from dhos_messages_api.helper.security import (
    create_message_protection,
    message_by_id_protection,
    sender_or_receiver_protection,
    sender_receiver_protection,
)
from dhos_messages_api.models.api_spec import MessagePatchRequest

api_blueprint = flask.Blueprint("messages", __name__)


@api_blueprint.route("/dhos/v1/message", methods=["POST"])
@protected_route(
    or_(
        scopes_present(required_scopes="write:gdm_message_all"),
        and_(
            scopes_present(required_scopes="write:gdm_message"),
            create_message_protection,
        ),
    )
)
@deprecated_route(superseded_by="POST /dhos/v2/message")
def create_message_v1() -> Response:
    """---
    post:
      summary: Create new message
      description: Create a new message using the details provided in the request body.
      tags: [message]
      deprecated: true
      parameters:
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      requestBody:
        description: JSON body containing the message
        required: true
        content:
          application/json:
            schema: MessageRequest
      responses:
        '200':
          description: The new message
          content:
            application/json:
              schema: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    message_details = connexion.request.get_json()
    response = controller.create_message(message_details=message_details)
    return flask.jsonify(response)


@api_blueprint.route("/dhos/v2/message", methods=["POST"])
@protected_route(
    or_(
        scopes_present(required_scopes="write:gdm_message_all"),
        and_(
            scopes_present(required_scopes="write:gdm_message"),
            create_message_protection,
        ),
    )
)
def create_message() -> Response:
    """---
    post:
      summary: Create new message
      description: Create a new message using the details provided in the request body.
      tags: [message]
      parameters:
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      requestBody:
        description: JSON body containing the message
        required: true
        content:
          application/json:
            schema: MessageRequest
      responses:
        '200':
          description: The new message
          content:
            application/json:
              schema: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    message_details = connexion.request.get_json()
    response = controller.create_message(message_details=message_details)
    return flask.jsonify(response)


@api_blueprint.route("/dhos/v1/message/<message_id>", methods=["GET"])
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_message_all"),
        and_(
            scopes_present(required_scopes="read:gdm_message"), message_by_id_protection
        ),
    )
)
def get_message_by_uuid(message_id: str) -> Response:
    """
    ---
    get:
      summary: Get message
      description: Get a message by the UUID provided in the URL path.
      tags: [message]
      parameters:
        - name: message_id
          in: path
          required: true
          description: The message UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      responses:
        '200':
          description: The message
          content:
            application/json:
              schema: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return flask.jsonify(controller.get_message_by_uuid(message_id))


@api_blueprint.route("/dhos/v1/message/<message_id>", methods=["PATCH"])
@protected_route(
    or_(
        scopes_present(required_scopes="write:gdm_message_all"),
        and_(
            scopes_present(required_scopes="write:gdm_message"),
            message_by_id_protection,
        ),
    )
)
def update_message(message_id: str) -> Response:
    """
    ---
    patch:
      summary: Update message
      description: >-
        Update the message matching the UUID provided in the request path, using the fields provided in
        the request body.
      tags: [message]
      parameters:
        - name: message_id
          in: path
          required: true
          description: The message UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      requestBody:
        description: JSON body containing the message
        required: true
        content:
          application/json:
            schema: MessagePatchRequest
      responses:
        '200':
          description: The updated message
          content:
            application/json:
              schema: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    message_details = MessagePatchRequest().load(
        connexion.request.get_json(), unknown=RAISE
    )

    return flask.jsonify(controller.update_message(message_id, message_details))


@api_blueprint.route("/dhos/v1/sender/<sender_id>/message", methods=["GET"])
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_message_all"),
        and_(
            scopes_present(required_scopes="read:gdm_message"),
            sender_receiver_protection,
        ),
    )
)
def get_messages_by_sender_uuid(sender_id: str) -> Response:
    """
    ---
    get:
      summary: Get messages by sender
      description: Get a list of messages sent by the sender UUID provided in the URL path.
      tags: [message]
      parameters:
        - name: sender_id
          in: path
          required: true
          description: The sender UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      responses:
        '200':
          description: A list of messages sent by the sender
          content:
            application/json:
              schema:
                type: array
                items: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return flask.jsonify(controller.get_messages_by_sender_uuid(sender_id))


@api_blueprint.route("/dhos/v1/receiver/<receiver_id>/message", methods=["GET"])
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_message_all"),
        and_(
            scopes_present(required_scopes="read:gdm_message"),
            sender_receiver_protection,
        ),
    )
)
def get_messages_by_receiver_uuid(receiver_id: str) -> Response:
    """
    ---
    get:
      summary: Get messages by receiver
      description: >-
        Get a list of messages received by the receiver UUID provided in the URL path.

        Consumers of this endpoint who have the `read:gdm_message_all` permission will retrieve all
        messages received by the receiver.

        For all other consumers, this endpoint will only retrieve messages where the consumer of the
        endpoint is themselves the receiver - i.e. their JWT claims will need to show them as having
        the UUID that is passed in as the receiver_id parameter.
      tags: [message]
      parameters:
        - name: receiver_id
          in: path
          required: true
          description: The receiver UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      responses:
        '200':
          description: A list of messages received by the receiver
          content:
            application/json:
              schema:
                type: array
                items: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return flask.jsonify(controller.get_messages_by_receiver_uuid(receiver_id))


@api_blueprint.route("/dhos/v1/sender/<sender_id>/active/message", methods=["GET"])
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_message_all"),
        and_(
            scopes_present(required_scopes="read:gdm_message"),
            sender_receiver_protection,
        ),
    )
)
def get_active_messages_by_sender_uuid(sender_id: str) -> Response:
    """
    ---
    get:
      summary: Get active messages by sender
      description: Get a list of active messages sent by the sender UUID provided in the URL path.
      tags: [message]
      parameters:
        - name: sender_id
          in: path
          required: true
          description: The sender UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      responses:
        '200':
          description: A list of active messages sent by the sender
          content:
            application/json:
              schema:
                type: array
                items: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return flask.jsonify(controller.get_active_messages_by_sender_uuid(sender_id))


@api_blueprint.route("/dhos/v1/receiver/<receiver_id>/active/message", methods=["GET"])
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_message_all"),
        and_(
            scopes_present(required_scopes="read:gdm_message"),
            sender_receiver_protection,
        ),
    )
)
def get_active_messages_by_receiver_uuid(receiver_id: str) -> Response:
    """
    ---
    get:
      summary: Get active messages by receiver
      description: >-
        Get a list of active messages received by the receiver UUID in the URL path.

        Consumers of this endpoint who have the `read:gdm_message_all` permission will retrieve all
        active messages received by the receiver.

        For all other consumers, this endpoint will only retrieve active messages where the consumer
        of the endpoint is themselves the receiver - i.e. their JWT claims will need to show them as
        having the UUID that is passed in as the receiver_id parameter.
      tags: [message]
      parameters:
        - name: receiver_id
          in: path
          required: true
          description: The receiver UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      responses:
        '200':
          description: A list of active messages received by the receiver
          content:
            application/json:
              schema:
                type: array
                items: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return flask.jsonify(controller.get_active_messages_by_receiver_uuid(receiver_id))


@api_blueprint.route("/dhos/v1/sender_or_receiver/<unique_id>/message", methods=["GET"])
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_message_all"),
        scopes_present(required_scopes="read:message_all"),
        and_(
            scopes_present(required_scopes="read:gdm_message"),
            sender_or_receiver_protection,
        ),
    )
)
def get_messages_by_sender_uuid_or_receiver_uuid(unique_id: str) -> Response:
    """
    ---
    get:
      summary: Get messages by sender or receiver
      description: >-
        Get a list of messages sent by the sender or received by the receiver who matches
        the UUID provided in the URL path.
      tags: [message]
      parameters:
        - name: unique_id
          in: path
          required: true
          description: The sender UUID or receiver UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      responses:
        '200':
          description: A list of messages sent by the sender or received by the receiver
          content:
            application/json:
              schema:
                type: array
                items: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return flask.jsonify(
        controller.get_messages_by_sender_uuid_or_receiver_uuid(unique_id)
    )


@api_blueprint.route(
    "/dhos/v1/sender/<sender_id>/receiver/<receiver_id>/message", methods=["GET"]
)
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_message_all"),
        and_(
            scopes_present(required_scopes="read:gdm_message"),
            sender_receiver_protection,
        ),
    )
)
def get_messages_by_sender_uuid_and_receiver_uuid(
    sender_id: str, receiver_id: str
) -> Response:
    """
    ---
    get:
      summary: Get messages by sender and receiver
      description: >-
        Get a list of messages sent by the sender UUID and received by the receiver UUID, both of
        which should be provided in the URL path.
      tags: [message]
      parameters:
        - name: sender_id
          in: path
          required: true
          description: The sender UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
        - name: receiver_id
          in: path
          required: true
          description: The receiver UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      responses:
        '200':
          description: A list of messages sent by the sender and received by the receiver
          content:
            application/json:
              schema:
                type: array
                items: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return flask.jsonify(
        controller.get_messages_by_sender_uuid_and_receiver_uuid(sender_id, receiver_id)
    )


@api_blueprint.route(
    "/dhos/v1/sender/<sender_id>/receiver/<receiver_id>/active/message", methods=["GET"]
)
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_message_all"),
        and_(
            scopes_present(required_scopes="read:gdm_message"),
            sender_receiver_protection,
        ),
    )
)
def get_active_messages_by_sender_uuid_and_receiver_uuid(
    sender_id: str, receiver_id: str
) -> Response:
    """
    ---
    get:
      summary: Get active messages by sender and receiver
      description: >-
        Get a list of active messages sent by the sender UUID and received by the receiver UUID,
        both of which should be provided in the URL path.
      tags: [message]
      parameters:
        - name: sender_id
          in: path
          required: true
          description: The sender UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
        - name: receiver_id
          in: path
          required: true
          description: The receiver UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      responses:
        '200':
          description: A list of active messages sent by the sender and received by the receiver
          content:
            application/json:
              schema:
                type: array
                items: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return flask.jsonify(
        controller.get_active_messages_by_sender_uuid_and_receiver_uuid(
            sender_id, receiver_id
        )
    )


@api_blueprint.route(
    "/dhos/v1/receiver/<receiver_id>/active/callback/message", methods=["GET"]
)
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_message_all"),
        and_(
            scopes_present(required_scopes="read:gdm_message"),
            sender_receiver_protection,
        ),
    )
)
def get_active_callback_messages_by_receiver_uuid(receiver_id: str) -> Response:
    """
    ---
    get:
      summary: Get active callback messages by receiver
      description: >-
        Get a list of active callback messages received by the receiver UUID provided in the URL
        path.

        Consumers of this endpoint who have the `read:gdm_message_all` permission will retrieve all
        active callback messages received by the receiver.

        For all other consumers, this endpoint will only retrieve active callback messages where the
        consumer of the endpoint is themselves the receiver - i.e. their JWT claims will need to
        show them as having the UUID that is passed in as the receiver_id parameter.
      tags: [message]
      parameters:
        - name: receiver_id
          in: path
          required: true
          description: The receiver UUID
          schema:
            type: string
            example: '18439f36-ffa9-42ae-90de-0beda299cd37'
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      responses:
        '200':
          description: A list of active callback messages received by the receiver
          content:
            application/json:
              schema:
                type: array
                items: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return flask.jsonify(
        controller.get_active_callback_messages_by_receiver_uuid(receiver_id)
    )


@api_blueprint.route("/dhos/v1/active/callback/message", methods=["POST"])
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_patient_all"),
        scopes_present(required_scopes="read:gdm_patient"),
    )
)
def get_active_callback_messages_for_patients() -> Response:
    """
    ---
    post:
      summary: Get active callback messages for patients
      description: >-
        Get a list of active callback messages sent by all of the patient UUIDs provided in the
        request body.

        You must have either "read:gdm_patient_all" or "read:gdm_patient" to get messages from this
        endpoint.
      tags: [message]
      parameters:
        - in: header
          name: X-Location-Ids
          description: List of location UUIDs, only used for clinicians
          schema:
            type: string
            example: '09db61d2-2ad9-4878-beee-1225b720c205,5d68b104-38cb-48fe-a814-00ac1387ef17'
          required: false
      requestBody:
        description: JSON body containing the list of patients
        required: true
        content:
          application/json:
            schema:
              type: array
              items:
                type: string
                example: '18439f36-ffa9-42ae-90de-0beda299cd37'
      responses:
        '200':
          description: A list of active callback messages for the list of patient UUIDs
          content:
            application/json:
              schema:
                type: array
                items: MessageResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    patient_list = connexion.request.get_json()

    return flask.jsonify(
        controller.get_active_callback_messages_for_patients(patient_list)
    )
