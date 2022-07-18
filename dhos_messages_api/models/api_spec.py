from typing import TypedDict

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask_batteries_included.helpers.apispec import (
    FlaskBatteriesPlugin,
    Identifier,
    initialise_apispec,
    openapi_schema,
)
from marshmallow import EXCLUDE, Schema, fields, validate
from marshmallow.validate import OneOf

from dhos_messages_api.blueprint_api.controller import DhosMessageType

dhos_messages_api_spec: APISpec = APISpec(
    version="1.2.0",
    openapi_version="3.0.3",
    title="DHOS Messages API",
    info={
        "description": "The DHOS Messages API is responsible for storing and retrieving messages."
    },
    plugins=[FlaskPlugin(), MarshmallowPlugin(), FlaskBatteriesPlugin()],
)

initialise_apispec(dhos_messages_api_spec)
not_empty = validate.Length(min=1)


@openapi_schema(dhos_messages_api_spec)
class MessageTypeSchema(Schema):
    class Meta:
        title = "Message Type schema fields"
        unknown = EXCLUDE
        ordered = True

        class Dict(TypedDict, total=False):
            value: int

    value = fields.Int(
        required=True,
        example=1,
        description="The type of the message",
        validate=OneOf([type_.value for type_ in DhosMessageType]),
    )


@openapi_schema(dhos_messages_api_spec)
class MessageSchema(Schema):
    class Meta:
        title = "Message fields common to request and response"
        unknown = EXCLUDE
        ordered = True

        class Dict(TypedDict, total=False):
            sender: str
            sender_type: str
            receiver: str
            receiver_type: str
            message_type: MessageTypeSchema.Meta.Dict
            content: str

    sender = fields.String(
        required=True,
        example="74780805-0a75-4bc3-99fb-3e3a64986cac",
        description="The UUID of the sender",
    )
    sender_type = fields.String(
        required=True,
        example="clinician",
        description="The type of the sender",
    )
    receiver = fields.String(
        required=True,
        example="74780805-0a75-4bc3-99fb-3e3a64986cac",
        description="The UUID of the receiver",
    )
    receiver_type = fields.String(
        required=True,
        example="patient",
        description="The type of the receiver",
    )
    message_type = fields.Nested(
        MessageTypeSchema,
        required=True,
    )
    content = fields.String(
        required=True,
        example="Please call me at your earliest convenience.",
        description="The content of the message",
    )


@openapi_schema(dhos_messages_api_spec)
class MessageRequest(MessageSchema):
    class Meta:
        title = "Message request"
        unknown = EXCLUDE
        ordered = True

        class Dict(TypedDict, MessageSchema.Meta.Dict, total=False):
            pass


@openapi_schema(dhos_messages_api_spec)
class MessageResponse(MessageSchema, Identifier):
    class Meta:
        title = "Message response"
        unknown = EXCLUDE
        ordered = True

        class Dict(TypedDict, MessageSchema.Meta.Dict, total=False):
            pass


@openapi_schema(dhos_messages_api_spec)
class MessagePatchRequest(Schema):
    class Meta:
        title = "Message PATCH request"
        ordered = True

        class Dict(TypedDict, total=False):
            retrieved: str
            confirmed: str
            confirmed_by: str
            related_message: str
            cancelled: str
            cancelled_by: str

    retrieved = fields.String(
        required=False,
        example="2018-02-11T11:59:50.123+03:00",
        description="The timezone-aware timestamp at which the message was retrieved",
        validate=not_empty,
    )
    confirmed = fields.String(
        required=False,
        example="2018-02-12T09:44:40.456+03:00",
        description="The timezone-aware timestamp at which the message was confirmed",
        validate=not_empty,
    )
    confirmed_by = fields.String(
        required=False,
        example="ac8459b0-6a9a-4e8e-a2de-41c5dd9b81aa",
        description="The UUID of the user who confirmed the message",
        validate=not_empty,
    )
    related_message = fields.String(
        required=False,
        example="ac8459b0-6a9a-4e8e-a2de-41c5dd9b81aa",
        description="The UUID of the related message",
        validate=not_empty,
    )
    cancelled = fields.String(
        required=False,
        example="2018-02-13T07:23:30.789+03:00",
        description="The timezone-aware timestamp at which the message was cancelled",
        validate=not_empty,
    )
    cancelled_by = fields.String(
        required=False,
        example="ac8459b0-6a9a-4e8e-a2de-41c5dd9b81aa",
        description="The UUID of the user who cancelled the message",
        validate=not_empty,
    )
