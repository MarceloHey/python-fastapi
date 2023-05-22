from sqlalchemy import func
from .. import models, schemas, oAuth2
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional

router = APIRouter(
    prefix="/orm-posts",
    tags=['Posts']
)


@router.get('/', response_model=List[schemas.PostOut])
def ORMgetPosts(db: Session = Depends(get_db), limit: int = 10, offset=0, search: Optional[str] = ""):

    results = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(
        offset).all()

    return results


@router.get('/{id}', response_model=schemas.PostOut)
def ORMgetPost(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    return post


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def ORMcreatePost(post: schemas.PostCreate, db: Session = Depends(get_db), currentUser=Depends(oAuth2.getCurrentUser)):
    # unpack the dict, like JS destruct operator ({...random object})
    # print(**post.dict())

    newPost = models.Post(owner_id=currentUser.id, **post.dict())

    db.add(newPost)
    db.commit()
    db.refresh(newPost)

    return newPost


@router.put('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def ORMupdatePost(id: int, updatedPost: schemas.PostCreate, db: Session = Depends(get_db), currentUser=Depends(oAuth2.getCurrentUser)):

    postQuery = db.query(models.Post).filter(models.Post.id == id)
    post = postQuery.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    if post.owner_id != int(currentUser.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized")

    postQuery.update(updatedPost.dict(), synchronize_session=False)
    db.commit()

    return postQuery.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def ORMdeletePost(id: int, db: Session = Depends(get_db), currentUser=Depends(oAuth2.getCurrentUser)):

    toDelete = db.query(models.Post).filter(models.Post.id == id)

    if toDelete.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    if toDelete.first().owner_id != int(currentUser.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized")

    toDelete.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

  # ROTAS NORMAIS

# @router.get('/posts')
# def getPosts():
#     cursor.execute(""" SELECT * FROM posts """)
#     posts = cursor.fetchall()
#     return posts


# @router.get('/posts/{id}')
# def getPost(id: int):
#     cursor.execute(
#         """ SELECT * FROM posts WHERE id = %s""", (str(id)))
#     post = cursor.fetchone()

#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with id: {id} was not found")

#     return post


# @router.post('/posts', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
# def createPost(post: schemas.PostCreate):
#     cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
#                    (post.title, post.content, post.published))
#     newPost = cursor.fetchone()
#     conn.commit()

#     return newPost


# @router.put('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
# def updatePost(id: int, post: schemas.PostCreate):
#     cursor.execute(
#         """ UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
#         (post.title, post.content, post.published, id))
#     updatedPost = cursor.fetchone()
#     conn.commit()

#     if updatedPost == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with id: {id} was not found")

#     return Response(status_code=status.HTTP_204_NO_CONTENT)


# @router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def deletePost(id: int):
#     cursor.execute(
#         """ DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
#     deletedPost = cursor.fetchone()
#     conn.commit()

#     if deletedPost == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with id: {id} was not found")

#     return Response(status_code=status.HTTP_204_NO_CONTENT)
