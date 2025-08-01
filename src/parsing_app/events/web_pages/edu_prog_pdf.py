import logging
import pathlib

import requests
import tqdm

import registration
import settings
import logs
import text_extractor
import database.dao as dao
import database.models as models


__all__ = []


@registration.run(
    delay_time=7 * 24 * 3600,
    endless_execution=True,
)
@logs.log_start_end
def parsing_ep_pdf():
    ep_dao = dao.EducationalProgramDAO()
    pdf_ep_dao = dao.PDFEducationalProgramDAO()
    pdf_ep_dao.delete_all()
    eps: list[models.EducationalProgramModel] = ep_dao.select_all()
    for ep in tqdm.tqdm(eps):
        response = requests.get(ep.link_pdf)
        name_file = pathlib.Path(ep.link_pdf.split('/')[-1])
        path_pdf = settings.PATH_PDF_EDUCATIONAL_PROGRAM / name_file
        with open(path_pdf, 'wb') as file:
            file.write(response.content)

        text_pdf = text_extractor.PyPDF2Extractor(path_pdf).get_text()
        pdf_ep_dao.create(
            educational_program=ep,
            path_pdf=str(path_pdf),
            text_pdf=text_pdf,
        )
