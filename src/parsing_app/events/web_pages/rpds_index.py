import logging
import collections

import bs4
import requests
import sqlalchemy.exc

import logs
import registration
import database.dao as dao
import database.models as models


__all__ = []


@registration.run(
    delay_time=7 * 24 * 3600,
    endless_execution=True,
)
@logs.log_start_end
def parsing_rpds_index():
    ep_dao = dao.EducationalProgramDAO()
    rpd_dao = dao.RPDDAO()
    rpd_dao.delete_all()
    edu_progs: list[models.EducationalProgramModel] = ep_dao.select_all()
    for edu_prog in edu_progs:
        parsing_rpd_index(edu_prog)


def parsing_rpd_index(edu_prog: models.EducationalProgramModel):
    rpd_dao = dao.RPDDAO()
    response = requests.get(edu_prog.link_rpds_page, allow_redirects=True)
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    all_links = soup.find_all('a')
    groups = collections.defaultdict(list)
    for link in all_links:
        for i in range(len(link.text)):
            if link.text[i].isdigit():
                break

        groups[link.text[:i]].append(link.get('href'))

    all_actual_links = [max(group) for group in groups.values()]
    global_all_links = [
        edu_prog.link_rpds_page.replace('list.php', link)
        for link in all_actual_links
    ]
    for global_link in global_all_links:
        if not global_link.endswith('.pdf'):
            logging.error(
                f'Ссылка на РПД не содержит ".pdf". {global_link}',
            )
            continue

        try:
            rpd_dao.create(
                link_pdf=global_link,
                educational_program=edu_prog,
            )
        except sqlalchemy.exc.IntegrityError:
            logging.warning(f'Link: {global_link}, you are present.')
