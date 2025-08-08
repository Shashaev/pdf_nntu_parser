import logging

import tqdm

import registration
import logs
import converters.link_block as link_block
import database.dao as dao
import settings


__all__ = []


@registration.run(
    delay_time=7 * 24 * 3600,
    endless_execution=True,
)
@logs.log_start_end
def parsing_blocks_of_links():
    if (
        settings.API_CATALOG is None
        or settings.API_TOCKEN is None
    ):
        logging.error(
            'Для работы нужно предоставить в '
            'переменный окружение парамтеры: API_CATALOG, API_TOCKEN',
        )
        return

    link_rpd_dao = dao.LinkRPDDAO()
    rpd_dao = dao.RPDDAO()
    link_rpd_dao.delete_all()
    all_rpd = rpd_dao.select_all()
    for rpd in tqdm.tqdm(all_rpd):
        text_link_block = rpd_dao.get_text_link_block_by_rpd(rpd)
        if text_link_block is None:
            continue

        links = link_block.LinkBlock().parsing(text_link_block.text)
        for link in links:
            try:
                link_rpd_dao.create(
                    rpd=rpd,
                    **link.model_dump(),
                )
            except Exception as e:
                logging.error(
                    'Ошибка сохраниня связей в БД.'
                    f'\n{link = }'
                )
