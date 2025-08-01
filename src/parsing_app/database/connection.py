import sqlalchemy
import sqlalchemy.orm as orm

import settings
import database.models as models


__all__ = []

engin = sqlalchemy.create_engine(settings.CONNECTION_STRING)


def create_db_and_tables():
    models.Base.metadata.create_all(engin)


def drop_db():
    models.Base.metadata.drop_all(engin)


Session = orm.sessionmaker(engin)


def db_connection(fun):
    def inner(*args, **kwargs):
        with Session() as session:
            return fun(*args, **kwargs, session=session)

    return inner
