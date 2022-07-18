import time
from typing import Dict, List

from flask import Blueprint, Response, current_app, jsonify, make_response, request
from flask_batteries_included.helpers.security import protected_route
from flask_batteries_included.helpers.security.endpoint_security import key_present

from .controller import create_messages, reset_database

development_blueprint = Blueprint("dev", __name__, template_folder="templates")


@development_blueprint.route("/drop_data", methods=["POST"])
@protected_route(key_present("system_id"))
def drop_data_route() -> Response:

    if current_app.config["ALLOW_DROP_DATA"] is not True:
        raise PermissionError("Cannot drop data in this environment")

    start = time.time()
    reset_database()
    total_time = time.time() - start

    return jsonify({"complete": True, "time_taken": str(total_time) + "s"})


@development_blueprint.route("/create_messages", methods=["POST"])
@protected_route(key_present("system_id"))
def create_messages_route() -> Response:

    messages_details: List = request.get_json() or []
    create_messages(messages_details=messages_details)
    return make_response("", 201)
