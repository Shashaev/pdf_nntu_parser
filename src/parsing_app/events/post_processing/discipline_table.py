import logging

import tqdm

import registration
import logs
import database.dao as dao
import database.models as models


__all__ = []

ALLOWED_CHARACTERS = set('123456789AB-')
FIELDS_TO_CHECK = [
    'format_control_exam',
    'format_control_test',
    'format_control_assessment_test',
    'format_control_course_project',
    'format_control_course_work',
    'format_control_control',
    'format_control_essay',
    'format_control_rgr',
]


@registration.run(
    delay_time=7 * 24 * 3600,
    endless_execution=True,
)
@logs.log_start_end
def post_processing_forms_education():
    row_discipline_table_dao = dao.RowDisciplineTableDAO()
    rows: list[models.RowDisciplineTable] = (
        row_discipline_table_dao.select_all()
    )
    for row in tqdm.tqdm(rows):
        for field in FIELDS_TO_CHECK:
            value: str = getattr(row, field)
            if value is None:
                continue

            value = value.replace(' ', '')
            if len(set(value) - ALLOWED_CHARACTERS) >= 1:
                row_discipline_table_dao.delete(row.id_model)
                logging.info(
                    'В форме контроля обнаружен недопустимые символы: '
                    f'{set(value) - ALLOWED_CHARACTERS}. Строку в БД удалена.',
                )
                continue

            if (
                len(value) == 3
                and value[0].isdigit()
                and value[1] == '-'
                and value[2].isdigit()
            ):
                value = ''.join(
                    [
                        str(el)
                        for el in range(
                            int(value[0]),
                            int(value[2]),
                        )
                    ]
                )

            new_value = ','.join(value)
            row_discipline_table_dao.update(
                row.id_model,
                **{field: new_value},
            )
