import typing

import pydantic


__all__ = []


class CalledFunction(pydantic.BaseModel):
    max_count: int = pydantic.Field(default=1, ge=0)
    delay_time: float = pydantic.Field(default=0, ge=0)
    endless_execution: bool = False
    fun: typing.Callable
    last_execution_time: float = 0

    def __str__(self):
        return f'CalledFunction({super().__str__()})'


class RowDisciplineTableScheme(pydantic.BaseModel):
    index: str = pydantic.Field(min_length=2)
    name: str = pydantic.Field(min_length=5)
    code: int = pydantic.Field(ge=0)
    format_control_exam: str | None = pydantic.Field(
        min_length=1, default=None,
    )
    format_control_test: str | None = pydantic.Field(
        min_length=1, default=None,
    )
    format_control_assessment_test: str | None = pydantic.Field(
        min_length=1, default=None,
    )
    format_control_course_project: str | None = pydantic.Field(
        min_length=1, default=None,
    )
    format_control_course_work: str | None = pydantic.Field(
        min_length=1, default=None,
    )
    format_control_control: str | None = pydantic.Field(
        min_length=1, default=None,
    )
    format_control_essay: str | None = pydantic.Field(
        min_length=1, default=None,
    )
    format_control_rgr: str | None = pydantic.Field(min_length=1, default=None)

    class Config:
        from_attributes = True


class DescriptionRPDScheme(pydantic.BaseModel):
    index: str = pydantic.Field(min_length=2, max_length=20)
    # name: str = pydantic.Field(min_length=5)


class LinkRPDScheme(pydantic.BaseModel):
    link_type: typing.Literal[-1, 0, 1]
    link_from: str = pydantic.Field(min_length=3)
    link_to: str = pydantic.Field(min_length=3)

    class Config:
        from_attributes = True


class AbstractDescriptionRPDScheme(pydantic.BaseModel):
    id_model: int = pydantic.Field(ge=0)
    text_link_block: str | None = pydantic.Field(min_length=10)
    index: str | None = pydantic.Field(min_length=2)
