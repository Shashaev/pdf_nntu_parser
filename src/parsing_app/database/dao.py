import sqlalchemy.orm as orm

import database.models as models
import database.connection as connection
import parsing_app.schemes as schemes


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

    @connection.db_connection
    def get_rpds_by_id_ep(
        self,
        id_ep: int,
        session: orm.Session = None,
    ) -> list[models.RPDModel]:
        ep = (
            session.query(models.EducationalProgramModel)
            .filter_by(id_model=id_ep)
            .first()
        )
        if ep is None:
            return None

        return ep.rpds


class PDFEducationalProgramDAO(BaseDAO):
    model = models.PDFEducationalProgramModel

    def __init__(self):
        super().__init__(self.model)

    @connection.db_connection
    def get_by_ep_id(
        self,
        ep_id: int,
        session: orm.Session = None,
    ) -> models.PDFEducationalProgramModel | None:
        return (
            session.query(models.PDFEducationalProgramModel)
            .filter_by(educational_program_id=ep_id)
            .first()
        )


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

    @connection.db_connection
    def get_text_link_block_by_rpd(
        self,
        rpd: models.RPDModel,
        session: orm.Session = None,
    ) -> models.TextLinkBlockModel:
        return (
            session.query(models.TextLinkBlockModel)
            .filter_by(rpd_id=rpd.id_model)
            .first()
        )

    @connection.db_connection
    def get_dis_links_by_id_rpd(
        self,
        id_rpd: int,
        session: orm.Session = None,
    ) -> list[models.LinkRPDModel] | None:
        rpd = (
            session.query(models.RPDModel)
            .filter_by(id_model=id_rpd)
            .first()
        )
        if rpd is None:
            return None

        dis_links = rpd.links
        return dis_links

    @connection.db_connection
    def get_descriptions_by_id_ep(
        self,
        id_ep: int,
        session: orm.Session = None,
    ) -> list[schemes.AbstractDescriptionRPDScheme]:
        ep = (
            session
            .query(models.EducationalProgramModel)
            .filter_by(id_model=id_ep)
            .first()
        )
        if ep is None:
            return None

        rpds = ep.rpds
        if rpds is None:
            return None

        descriptions = []
        for rpd in rpds:
            id_model = rpd.id_model
            text_link_block = None
            index = None
            if rpd.text_link_block is not None:
                text_link_block = rpd.text_link_block.text

            if rpd.description_rpd is not None:
                index = rpd.description_rpd.index

            descriptions.append(
                schemes.AbstractDescriptionRPDScheme(
                    id_model=id_model,
                    text_link_block=text_link_block,
                    index=index,
                )
            )

        return descriptions


class PDFRPDDAO(BaseDAO):
    model = models.PDFRPDModel

    def __init__(self):
        super().__init__(self.model)

    @connection.db_connection
    def get_by_id_rpd(
        self,
        id_rpd: int,
        session: orm.Session = None,
    ):
        return (
            session.query(models.PDFRPDModel)
            .filter_by(rpd_id=id_rpd)
            .first()
        )


class DescriptionEPDAO(BaseDAO):
    model = models.DescriptionEPModel

    def __init__(self):
        super().__init__(self.model)

    @connection.db_connection
    def get_rows_by_ep_id(
        self,
        ep_id: int,
        session: orm.Session = None,
    ) -> list[models.DescriptionEPModel] | None:
        description = (
            session.query(models.DescriptionEPModel)
            .filter_by(educational_program_id=ep_id)
            .first()
        )
        if description is None:
            return None

        return description.rows_discipline_table


class RowDisciplineTableDAO(BaseDAO):
    model = models.RowDisciplineTable

    def __init__(self):
        super().__init__(self.model)


class DescriptionRPDDAO(BaseDAO):
    model = models.DescriptionRPDModel

    def __init__(self):
        super().__init__(self.model)


class TextLinkBlockDAO(BaseDAO):
    model = models.TextLinkBlockModel

    def __init__(self):
        super().__init__(self.model)


class LinkRPDDAO(BaseDAO):
    model = models.LinkRPDModel

    def __init__(self):
        super().__init__(self.model)
