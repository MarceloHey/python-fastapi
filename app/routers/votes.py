from email.policy import HTTP
from pyexpat import model
from .. import models, schemas, oAuth2
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from ..util import hash

router = APIRouter(
    prefix="/orm-vote",
    tags=['Vote']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), currentUser=Depends(oAuth2.getCurrentUser)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

    voteQuery = db.query(models.Vote).filter(models.Vote.post_id ==
                                             vote.post_id, models.Vote.user_id == int(currentUser.id))
    foundVote = voteQuery.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {vote.post_id} does not exists")

    if (vote.dir == 1):
        if (foundVote):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"User {currentUser.id} has already voted on post {vote.post_id}")

        newVote = models.Vote(post_id=vote.post_id,
                              user_id=int(currentUser.id))

        db.add(newVote)
        db.commit()
        return {"message": "Successfully added vote"}
    else:
        if not foundVote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Vote does not exist")

        voteQuery.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully removed vote"}
