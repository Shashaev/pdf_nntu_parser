import logging

import tqdm

import registration
import logs
import database.dao as dao
import database.models as models
import converters.discipline_table as discipline_table


__all__ = []


@registration.run(
    delay_time=7 * 24 * 3600,
    endless_execution=True,
)
@logs.log_start_end
def title_page_ep_conversion():
    ep_dao = dao.EducationalProgramDAO()
    pdfs_ep: list[models.EducationalProgramModel] = ep_dao.select_all()
    row_discipline_table_dao = dao.RowDisciplineTableDAO()
    row_discipline_table_dao.delete_all()
    for edu_prog in tqdm.tqdm(pdfs_ep):
        pdf_ep = ep_dao.get_pdf_by_ep(edu_prog)
        description = ep_dao.get_description_by_ep(edu_prog)
        converter = discipline_table.DisciplineTable(pdf_ep)
        if not converter.is_exists_block():
            logging.error(f'Не найдена таблица дисциплин: {pdf_ep.path_pdf}')
            continue

        rows_discipline_table = []
        try:
            rows_discipline_table = converter.parsing()
        except BaseException as e:
            logging.error(e, f'Файл: {pdf_ep.path_pdf}')

        if len(rows_discipline_table) <= 5:
            logging.error(
                'Подозрительно малое кол-во строк в таблице выявлено '
                f'({len(rows_discipline_table) = }). Файл: {pdf_ep.path_pdf}',
            )
            continue

        for row_discipline_table in rows_discipline_table:
            row_discipline_table_dao.create(
                description_ep=description,
                **row_discipline_table.model_dump(),
            )
