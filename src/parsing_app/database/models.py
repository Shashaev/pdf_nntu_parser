import typing
import datetime

import sqlalchemy
import sqlalchemy.orm as orm


__all__ = []


class Base(orm.DeclarativeBase):
    pass


class ModelWithPK(Base):
    __abstract__ = True

    id_model: orm.Mapped[int] = orm.mapped_column(primary_key=True)


all_forms_education = typing.Literal['Очная', 'Очно-заочная', 'Заочная']
all_levels_educational = typing.Literal[
    'Специалитет',
    'Бакалавриат',
    'Магистратура',
    'Аспирантура',
]


class EducationalProgramModel(ModelWithPK):
    __tablename__ = 'EducationalProgram'

    link_pdf: orm.Mapped[str] = orm.mapped_column(unique=True)
    link_rpds_page: orm.Mapped[str] = orm.mapped_column(unique=True)
    pdf: orm.Mapped[typing.Optional['PDFEducationalProgramModel']] = (
        orm.relationship(
            back_populates='educational_program',
        )
    )
    rpds: orm.Mapped[typing.Optional[list['RPDModel']]] = orm.relationship(
        back_populates='educational_program',
    )
    description: orm.Mapped[typing.Optional['DescriptionEPModel']] = (
        orm.relationship(
            back_populates='educational_program',
        )
    )


class DescriptionEPModel(ModelWithPK):
    __tablename__ = 'DescriptionEPModel'

    educational_program_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('EducationalProgram.id_model'),
    )
    educational_program: orm.Mapped[EducationalProgramModel] = (
        orm.relationship(
            'EducationalProgramModel',
            back_populates='description',
        )
    )
    form_education: orm.Mapped[all_forms_education | None]
    level: orm.Mapped[all_levels_educational | None]
    code: orm.Mapped[str | None]
    name: orm.Mapped[str | None]
    profile: orm.Mapped[str | None]
    date_approval: orm.Mapped[datetime.date | None]
    rows_discipline_table: orm.Mapped[list['RowDisciplineTable'] | None] = (
        orm.relationship(
            back_populates='description_ep',
        )
    )


class RowDisciplineTable(ModelWithPK):
    __tablename__ = 'RowDisciplineTable'

    description_ep_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('DescriptionEPModel.id_model'),
    )
    description_ep: orm.Mapped[DescriptionEPModel] = orm.relationship(
        'DescriptionEPModel',
        back_populates='rows_discipline_table',
    )
    index: orm.Mapped[str]
    name: orm.Mapped[str]
    code: orm.Mapped[int]
    format_control_exam: orm.Mapped[typing.Optional[str]]
    format_control_test: orm.Mapped[typing.Optional[str]]
    format_control_assessment_test: orm.Mapped[typing.Optional[str]]
    format_control_course_project: orm.Mapped[typing.Optional[str]]
    format_control_course_work: orm.Mapped[typing.Optional[str]]
    format_control_control: orm.Mapped[typing.Optional[str]]
    format_control_essay: orm.Mapped[typing.Optional[str]]
    format_control_rgr: orm.Mapped[typing.Optional[str]]


class PDFEducationalProgramModel(ModelWithPK):
    __tablename__ = 'PDFEducationalProgramModel'

    educational_program_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('EducationalProgram.id_model'),
    )
    educational_program: orm.Mapped[EducationalProgramModel] = (
        orm.relationship(
            'EducationalProgramModel',
            back_populates='pdf',
        )
    )
    path_pdf: orm.Mapped[str] = orm.mapped_column(unique=True)
    text_pdf: orm.Mapped[str]


class RPDModel(ModelWithPK):
    __tablename__ = 'RPDModel'

    educational_program_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('EducationalProgram.id_model'),
    )
    educational_program: orm.Mapped[EducationalProgramModel] = (
        orm.relationship(
            'EducationalProgramModel',
            back_populates='rpds',
        )
    )
    link_pdf: orm.Mapped[str]
    pdf: orm.Mapped[typing.Optional['PDFRPDModel']] = orm.relationship(
        back_populates='rpd'
    )
    description_rpd: orm.Mapped[typing.Optional['DescriptionRPDModel']] = (
        orm.relationship(back_populates='rpd')
    )


class PDFRPDModel(ModelWithPK):
    __tablename__ = 'PDFRPDModel'

    rpd_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('RPDModel.id_model'),
    )
    rpd: orm.Mapped[RPDModel] = orm.relationship(
        'RPDModel',
        back_populates='pdf',
    )
    path_pdf: orm.Mapped[str] = orm.mapped_column(unique=True)
    text_pdf: orm.Mapped[str]


class DescriptionRPDModel(ModelWithPK):
    __tablename__ = 'DescriptionRPDModel'

    rpd_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('RPDModel.id_model'),
    )
    rpd: orm.Mapped[RPDModel] = orm.relationship(
        'RPDModel',
        back_populates='description_rpd',
    )
    index: orm.Mapped[str]
    # name: orm.Mapped[str]
