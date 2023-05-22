from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oAuthScheme = OAuth2PasswordBearer(tokenUrl='login')


def createAccessToken(data: dict):
    toEncode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    toEncode.update({"exp": expire})

    encodedJWT = jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)

    return encodedJWT


def verifyAccessToken(token: str, credentialsException):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("userId")

        if id is None:
            raise credentialsException

        tokenData = schemas.TokenData(id=id)
    except JWTError:
        raise credentialsException

    return tokenData


def getCurrentUser(token: str = Depends(oAuthScheme)):
    credentialsException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail=f"Could not validade credentials", headers={"WWW-Authenticate": "Bearer"})
    return verifyAccessToken(token=token, credentialsException=credentialsException)
