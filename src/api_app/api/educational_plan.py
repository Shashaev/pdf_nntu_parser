import os
import http

import fastapi
import fastapi.responses as responses

import parsing_app.database.dao as dao
import parsing_app.database.models as models
import parsing_app.schemes
import schemes.educational_plan


router = fastapi.APIRouter(
    prefix='/educational_plan',
    tags=['Учебные планы'],
)


@router.get('/links')
def get_links() -> list[str]:
    ep_dao = dao.EducationalProgramDAO()
    eps: list[models.EducationalProgramModel] = ep_dao.select_all()
    links = [ep.link_pdf for ep in eps]
    return links


@router.get('/descriptions')
def get_descriptions() -> list[
    schemes.educational_plan.DescriptionEducationalPlanScheme
]:
    description_dao = dao.DescriptionEPDAO()
    models_description: models.DescriptionEPModel = description_dao.select_all()
    descriptions = [
        schemes.educational_plan.DescriptionEducationalPlanScheme.model_validate(
            description
        )
        for description in models_description
    ]
    return descriptions


@router.get(
    '/pdf/{id_ep}',
)
def get_pdf(id_ep: int) -> responses.FileResponse:
    pdf_ep_dao = dao.PDFEducationalProgramDAO()
    pdf_model = pdf_ep_dao.get_by_ep_id(id_ep)
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


@router.get('/pdf_text/{id_ep}')
def get_pdf_text(id_ep: int) -> str:
    pdf_ep_dao = dao.PDFEducationalProgramDAO()
    pdf_model = pdf_ep_dao.get_by_ep_id(id_ep)
    if pdf_model is None or not pdf_model.text_pdf:
        return fastapi.Response(
            status_code=http.HTTPStatus.NOT_FOUND,
        )

    return pdf_model.text_pdf


@router.get('/discipline_table/{id_ep}')
def get_discipline_table(id_ep: int) -> list[parsing_app.schemes.RowDisciplineTableScheme]:
    description_dao = dao.DescriptionEPDAO()
    rows_models = description_dao.get_rows_by_ep_id(id_ep)
    if rows_models is None:
        return fastapi.Response(
            status_code=http.HTTPStatus.NOT_FOUND,
        )

    rows = [
        parsing_app.schemes.RowDisciplineTableScheme.model_validate(
            row,
        ) for row in rows_models
    ]
    return rows
