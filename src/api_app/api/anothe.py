import typing

import fastapi


router = fastapi.APIRouter(tags=['Другое'])


@router.get('/source')
def get_source() -> typing.Literal['https://www.nntu.ru/sveden/education/']:
    return 'https://www.nntu.ru/sveden/education/'
