from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, util, oAuth2


router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=schemas.AccessToken)
def login(userCredentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(
        models.User.email == userCredentials.username
    ).first()

    if user == None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")

    if not util.verifyPassword(userCredentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")

    # criar JWT TOKEN
    accessToken = oAuth2.createAccessToken(data={"userId": user.id})

    # retornar TOKEN
    return {"accessToken": accessToken, "tokenType": "bearer"}
