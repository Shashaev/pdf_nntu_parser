import http
import os

import fastapi
import fastapi.responses as responses

import parsing_app.database.dao as dao
import parsing_app.database.models as models
import parsing_app.schemes as schemes


router = fastapi.APIRouter(
    prefix='/rpd',
    tags=['РПД'],
)


@router.get('/page_links')
def get_page_links() -> list[str]:
    ep_dao = dao.EducationalProgramDAO()
    eps: list[models.EducationalProgramModel] = ep_dao.select_all()
    links = [ep.link_rpds_page for ep in eps]
    return links


@router.get('/links/{id_ep}')
def get_links(id_ep: int) -> list[str]:
    ep_dao = dao.EducationalProgramDAO()
    rpd_models = ep_dao.get_rpds_by_id_ep(id_ep)
    if rpd_models is None:
        return fastapi.Response(
            status_code=http.HTTPStatus.NOT_FOUND,
        )

    links = [rpd.link_pdf for rpd in rpd_models]
    return links


@router.get('/description/{id_ep}')
def get_description(id_ep: int) -> list[schemes.AbstractDescriptionRPDScheme]:
    rpd_dao = dao.RPDDAO()
    descriptions = rpd_dao.get_descriptions_by_id_ep(id_ep)
    if descriptions is None:
        return fastapi.Response(
            status_code=http.HTTPStatus.NOT_FOUND,
        )

    return descriptions


@router.get('/pdf/{id_rpd}')
def get_pdf(id_rpd: int) -> responses.FileResponse:
    pdf_rpd_dao = dao.PDFRPDDAO()
    pdf_model = pdf_rpd_dao.get_by_id_rpd(id_rpd)
    if pdf_model is None:
        return fastapi.Response(
            status_code=http.HTTPStatus.NOT_FOUND,
        )

    headers = {'Content-Disposition': f'attachment; filename="outfile.pdf"'}
    pdf_path = os.path.normpath(pdf_model.path_pdf)
    return responses.FileResponse(
        pdf_path,
        headers=headers,
        media_type='application/pdf',
    )


@router.get('/pdf_text/{id_rpd}')
def get_pdf(id_rpd: int) -> str:
    pdf_rpd_dao = dao.PDFRPDDAO()
    pdf_model = pdf_rpd_dao.get_by_id_rpd(id_rpd)
    if pdf_model is None:
        return fastapi.Response(
            status_code=http.HTTPStatus.NOT_FOUND,
        )

    return pdf_model.text_pdf


@router.get('/disciplinary_links/{id_rpd}')
def get_disciplinary_links(id_rpd: int) -> list[schemes.LinkRPDScheme]:
    rpd_dao = dao.RPDDAO()
    model_disciplinary_links = rpd_dao.get_dis_links_by_id_rpd(id_rpd)
    if model_disciplinary_links is None:
        return fastapi.Response(
            status_code=http.HTTPStatus.NOT_FOUND,
        )

    disciplinary_links = [
        schemes.LinkRPDScheme.model_validate(disciplinary_link)
        for disciplinary_link in model_disciplinary_links
    ]
    return disciplinary_links
