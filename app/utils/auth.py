import hashlib, os, binascii, jwt
import dataclasses
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from app.database import models as m
from sqlalchemy.sql import expression as sql_exp
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN
)
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.utils.ctx import AppCtx


_PBKDF2_HASH_NAME = "SHA256"
_PBKDF2_ITERATIONS = 100_000
user_auth_scheme = HTTPBearer()


@dataclasses.dataclass
class AuthUtilError(Exception):
    code: str
    message: str


_executor = ThreadPoolExecutor(10)


# DONE: sync to async
async def generate_hashed_password(password: str) -> str:
    def _inner(password: str) -> str:
        pbkdf2_salt = os.urandom(16)
        pw_hash = hashlib.pbkdf2_hmac(
            _PBKDF2_HASH_NAME,  #hash_name
            password.encode("utf-8"),  #password
            pbkdf2_salt,  #salt
            _PBKDF2_ITERATIONS,  # iterations
        )
        
        return "%s:%s" % (
            binascii.hexlify(pbkdf2_salt).decode("utf-8"),  # sep: str | bytes
            binascii.hexlify(pw_hash).decode("utf-8"),
        )

    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(
        _executor, 
        _inner, 
        password
    )



async def validate_hashed_password(password: str, hashed_password: str) -> bool:
    def _inner(password: str, hashed_password: str) -> bool:
        pbkdf2_salt_hex, pw_hash_hex = hashed_password.split(":")

        pw_challenge = hashlib.pbkdf2_hmac(
            _PBKDF2_HASH_NAME,  #hash_name
            password.encode("utf-8"),  #password
            binascii.unhexlify(pbkdf2_salt_hex),  #salt
            _PBKDF2_ITERATIONS,  # iterations
        )

        return pw_challenge == binascii.unhexlify(pw_hash_hex)

    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(
        _executor, 
        _inner, 
        password, 
        hashed_password,
    )


def validate_access_token(access_token: str) -> int:
    try:
        payload = jwt.decode(
            access_token, 
            "secret", 
            algorithms=["HS256"],
            issuer="fastapi-practice"
        )  # jwt 검증
    except jwt.ExpiredSignatureError:
        # 만료된 경우
        raise AuthUtilError(
            code="jwt_expired", 
            message="jwt expired please try reauthenticate"
        )
    except jwt.InvalidIssuerError:
        # 여기 토큰이 아닌 경우
        raise AuthUtilError(
            code="jwt_invalid_issuer",
            message="jwt token is not issued from this service"
        )
    except Exception:
        raise AuthUtilError(
            code="invalid_jwt",
            message="jwt is invalid"
        )

    user_id = payload.get("_id")
    if user_id is None:
        raise AuthUtilError(
            code="invalid_payload",
            message="payload is invalid",
        )
    
    return user_id


def resolve_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(user_auth_scheme)
) -> int:
    return validate_access_token(credentials.credentials)


async def validate_user_role(user_id: int, role: m.UserRoleEnum):
    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == user_id)
    )

    if user is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="user not found")

    if user.role < role:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You are not authorized to access. Please upgrade your role.",
        )