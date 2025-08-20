import logging

import bs4
import requests

import registration
import logs
import database.dao as dao


__all__ = []


@registration.run(
    delay_time=7 * 24 * 3600,
    endless_execution=True,
)
@logs.log_start_end
def parsing_education_index():
    url = 'https://www.nntu.ru/sveden/education/'
    response = requests.get(url, allow_redirects=True)
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    now_obj = soup.find(attrs={'id': 'eduop'}).find_next()
    ep_dao = dao.EducationalProgramDAO()
    ep_dao.delete_all()
    while now_obj := now_obj.find_next_sibling():
        try:
            number = now_obj.find_next()
            # number_int = int(number.text)
            # if not(3 <= number_int <= 8 or 26 <= number_int <= 27):
            #     continue
            identifier = number.find_next_sibling()
            specialties = identifier.find_next_sibling()
            education_level = specialties.find_next_sibling()
            profile = education_level.find_next_sibling()
            forms_education = profile.find_next_sibling()
            block_curriculum = (
                forms_education.find_next_sibling().find_next_sibling()
            )
            link_rpds_page = block_curriculum.find_next_sibling().find('a')
            all_links_to_curriculum = [
                link.get('href')
                for link in block_curriculum.find('div').find_all('a')
            ]
            link_pdf_ep = 'https://www.nntu.ru' + max(
                all_links_to_curriculum,
            )
            if '.pdf' not in link_pdf_ep:
                logging.error(
                    'Ссылка на ученбый план не содержит .pdf. '
                    f'{link_pdf_ep}',
                )
                continue

            ep_dao.create(
                link_pdf=link_pdf_ep,
                link_rpds_page='https://www.nntu.ru'
                + link_rpds_page.get('href'),
            )
        except BaseException as e:
            logging.error(e)
