# import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# import time
# from psycopg2.extras import RealDictCursor
from .config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""Tentar conexão com o banco até dar sucesso para continuar o programa (SEM ORM)"""
# while True:
#     try:
#         conn = psycopg2.connect(host="localhost", database="fastapi",
#                                 user="postgres", password="1234", cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print('Database connection was successfull !')
#         break
#     except Exception as error:
#         print(error)
#         time.sleep(2)
