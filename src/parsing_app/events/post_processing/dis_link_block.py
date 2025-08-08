import tqdm

import registration
import logs
import database.dao as dao
import database.models as models


__all__ = []


@registration.run(
    delay_time=7 * 24 * 3600,
    endless_execution=True,
)
@logs.log_start_end
def post_processing_dis_link_blocks():
    link_rpd_dao = dao.LinkRPDDAO()
    links_model: list[models.LinkRPDModel] = link_rpd_dao.select_all()
    for link_model in tqdm.tqdm(links_model):
        if (
            link_model.link_type != -1
            and link_model.link_from == link_model.link_to
        ):
            link_rpd_dao.delete(link_model.id_model)
