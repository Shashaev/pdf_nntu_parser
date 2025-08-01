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
def parsing_rpds_pdf():
    rpd_dao = dao.RPDDAO()
    pdf_rpf_dao = dao.PDFRPDDAO()
    pdf_rpf_dao.delete_all()
    rpds: list[models.RPDModel] = rpd_dao.select_all()
    for rpd in tqdm.tqdm(rpds):
        response = requests.get(rpd.link_pdf)

        identifier = '_'.join(rpd.link_pdf.split('/')[-3:-1])
        path_to_rpd_category = settings.PATH_PDF_RPD / identifier
        path_to_rpd_category.mkdir(exist_ok=True)

        name_file = rpd.link_pdf.split('/')[-1]
        path_pdf = path_to_rpd_category / name_file
        with open(path_pdf, 'wb') as file:
            file.write(response.content)

        text_pdf = text_extractor.PyPDF2Extractor(path_pdf).get_text()
        pdf_rpf_dao.create(
            rpd_id=rpd.id_model,
            path_pdf=str(path_pdf),
            text_pdf=text_pdf,
        )
