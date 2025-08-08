import datetime
import typing

import pydantic


all_forms_education = typing.Literal['Очная', 'Очно-заочная', 'Заочная']
all_levels_educational = typing.Literal[
    'Специалитет',
    'Бакалавриат',
    'Магистратура',
    'Аспирантура',
]


class DescriptionEducationalPlanScheme(pydantic.BaseModel):
    educational_program_id: int = pydantic.Field(ge=0)
    form_education: all_forms_education
    level: all_levels_educational
    code: str | None
    name: str | None
    profile: str | None
    date_approval: datetime.date | None

    class Config:
        from_attributes = True
