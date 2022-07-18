import uuid

from behave.runner import Context
from environs import Env
from jose import jwt as jose_jwt


def get_clinician_token(context: Context) -> str:
    if hasattr(context, "clinician_jwt"):
        return context.clinician_jwt
    env: Env = Env()
    hs_issuer: str = env.str("HS_ISSUER")
    proxy_url: str = env.str("PROXY_URL")
    clinician_jwt: str = jose_jwt.encode(
        {
            "metadata": {"clinician_id": str(uuid.uuid4())},
            "iss": hs_issuer,
            "aud": proxy_url + "/",
            "scope": env.str("CLINICIAN_JWT_SCOPE"),
            "exp": 9_999_999_999,
        },
        key=env.str("HS_KEY"),
        algorithm="HS512",
    )
    context.clinician_jwt = clinician_jwt
    return context.clinician_jwt


def get_patient_token(context: Context) -> str:
    if hasattr(context, "patient_jwt"):
        return context.patient_jwt
    env: Env = Env()
    hs_issuer: str = env.str("HS_ISSUER")
    proxy_url: str = env.str("PROXY_URL")
    patient_jwt: str = jose_jwt.encode(
        {
            "metadata": {"patient_id": str(uuid.uuid4())},
            "iss": hs_issuer,
            "aud": proxy_url + "/",
            "scope": env.str("PATIENT_JWT_SCOPE"),
            "exp": 9_999_999_999,
        },
        key=env.str("HS_KEY"),
        algorithm="HS512",
    )
    context.patient_jwt = patient_jwt
    return context.patient_jwt


def get_system_token(context: Context) -> str:
    if hasattr(context, "system_jwt"):
        return context.system_jwt
    env: Env = Env()
    hs_issuer: str = env.str("HS_ISSUER")
    proxy_url: str = env.str("PROXY_URL")
    system_jwt: str = jose_jwt.encode(
        {
            "metadata": {"system_id": "dhos-robot"},
            "iss": hs_issuer,
            "aud": proxy_url + "/",
            "scope": env.str("SYSTEM_JWT_SCOPE"),
            "exp": 9_999_999_999,
        },
        key=env.str("HS_KEY"),
        algorithm="HS512",
    )
    context.system_jwt = system_jwt
    return context.system_jwt


def get_cached_token_for_user_type(context: Context, user_type: str) -> str:
    return getattr(context, f"{user_type}_jwt")
