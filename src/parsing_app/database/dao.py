import sqlalchemy.orm as orm

import database.models as models
import database.connection as connection


__all__ = []


class BaseDAO:
    def __init__(self, model: models.Base):
        self.model = model

    @connection.db_connection
    def create(self, *args, session: orm.Session = None, **kwargs):
        new_model = self.model(*args, **kwargs)
        session.add(new_model)
        session.commit()

    @connection.db_connection
    def select(self, pk: int, session: orm.Session = None) -> models.Base:
        return session.get(self.model, pk)

    @connection.db_connection
    def select_all(
        self,
        session: orm.Session = None,
    ) -> list[models.Base]:
        return session.query(self.model).all()

    @connection.db_connection
    def update(self, pk, session: orm.Session = None, **kwargs):
        model = self.select(pk)
        for key in kwargs:
            setattr(model, key, kwargs[key])

        session.add(model)
        session.commit()

    @connection.db_connection
    def delete(self, pk: int, session: orm.Session = None):
        session.delete(self.select(pk))
        session.commit()

    @connection.db_connection
    def delete_all(self, session: orm.Session = None):
        session.query(self.model).delete()
        session.commit()


class EducationalProgramDAO(BaseDAO):
    model = models.EducationalProgramModel

    def __init__(self):
        super().__init__(self.model)

    @connection.db_connection
    def get_pdf_by_ep(
        self,
        ep: models.EducationalProgramModel,
        session: orm.Session = None,
    ):
        return (
            session.query(models.PDFEducationalProgramModel)
            .filter_by(educational_program_id=ep.id_model)
            .first()
        )

    @connection.db_connection
    def get_description_by_ep(
        self,
        ep: models.EducationalProgramModel,
        session: orm.Session = None,
    ):
        return (
            session.query(models.DescriptionEPModel)
            .filter_by(educational_program_id=ep.id_model)
            .first()
        )


class PDFEducationalProgramDAO(BaseDAO):
    model = models.PDFEducationalProgramModel

    def __init__(self):
        super().__init__(self.model)


class RPDDAO(BaseDAO):
    model = models.RPDModel

    def __init__(self):
        super().__init__(self.model)

    @connection.db_connection
    def get_pdf_by_rpd(
        self,
        rpd: models.RPDModel,
        session: orm.Session = None,
    ):
        return (
            session.query(models.PDFRPDModel)
            .filter_by(rpd_id=rpd.id_model)
            .first()
        )


class PDFRPDDAO(BaseDAO):
    model = models.PDFRPDModel

    def __init__(self):
        super().__init__(self.model)


class DescriptionEPDAO(BaseDAO):
    model = models.DescriptionEPModel

    def __init__(self):
        super().__init__(self.model)


class RowDisciplineTableDAO(BaseDAO):
    model = models.RowDisciplineTable

    def __init__(self):
        super().__init__(self.model)


class DescriptionRPDDAO(BaseDAO):
    model = models.DescriptionRPDModel

    def __init__(self):
        super().__init__(self.model)
