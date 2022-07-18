from behave import given
from behave.runner import Context
from helpers.jwt import get_system_token


@given("I have a valid system JWT")
def get_system_jwt(context: Context) -> None:
    jwt: str = get_system_token(context)
    assert jwt is not None
    context.system_jwt = jwt
