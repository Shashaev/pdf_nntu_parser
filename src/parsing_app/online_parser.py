import abc
import collections
import pathlib

import bs4
import requests

import information_classes
import settings


__all__ = []


class OnlineBaseParser(abc.ABC):
    @abc.abstractmethod
    def get_data(self) -> any:
        pass


class OnlineChangingParser(OnlineBaseParser):
    def __init__(self, link: str | None = None):
        self.link = None
        if link is not None:
            self.update_link(link)

    @abc.abstractmethod
    def update_link(self, link: str):
        pass


class OnlineEducationParser(OnlineBaseParser):
    url = 'https://www.nntu.ru/sveden/education/'

    def get_data(self) -> list[information_classes.EducationalProgram]:
        response = requests.get(self.url, allow_redirects=True)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        now_obj = soup.find(attrs={'id': 'eduop'}).find_next()
        edu_programs = []
        while now_obj := now_obj.find_next_sibling():
            try:
                number = now_obj.find_next()
                identifier = number.find_next_sibling()
                specialties = identifier.find_next_sibling()
                education_level = specialties.find_next_sibling()
                profile = education_level.find_next_sibling()
                forms_education = profile.find_next_sibling()
                block_curriculum = (
                    forms_education.find_next_sibling().find_next_sibling()
                )
                links_to_work_programs = (
                    block_curriculum.find_next_sibling().find('a')
                )

                all_links_to_curriculum = [
                    link.get('href')
                    for link in block_curriculum.find('div').find_all('a')
                ]
                link_to_curriculum = 'https://www.nntu.ru' + max(
                    all_links_to_curriculum,
                )
                if '.pdf' not in link_to_curriculum:
                    print(
                        'Ссылка на ученбый план не содержит .pdf. '
                        f'{link_to_curriculum}',
                    )
                    continue

                response_file = requests.get(link_to_curriculum)
                name_file = pathlib.Path(
                    f'{identifier.text}_{profile.text}'
                    f'_{forms_education.text}.pdf',
                )
                path_to_curriculum = (
                    settings.PATH_PDF_EDUCATIONAL_PROGRAM / name_file
                )
                with open(path_to_curriculum, 'wb') as file:
                    file.write(response_file.content)

                edu_programs.append(
                    information_classes.EducationalProgram(
                        int(number.text),
                        identifier.text,
                        specialties.text,
                        education_level.text,
                        profile.text,
                        forms_education.text,
                        path_to_curriculum,
                        'https://www.nntu.ru'
                        + links_to_work_programs.get('href'),
                    ),
                )
            except BaseException as e:
                print(e)

        return edu_programs


class OnlineRPDParser(OnlineChangingParser):
    def __init__(self, identifier: str | None = None, link: str | None = None):
        super().__init__(link)
        self.identifier = None
        if identifier is not None:
            self.update_identifier(identifier)

    def update_link(self, link: str):
        if type(link) is not str:
            raise ValueError

        if not link.startswith('https://www.nntu.ru/sveden/files/rpd/'):
            print(link)
            raise ValueError

        self.link = link

    def update_identifier(self, identifier: str):
        if not identifier:
            raise ValueError

        self.identifier = identifier

    def get_data(self) -> list[pathlib.Path]:
        if not self.link or not self.identifier:
            raise FileNotFoundError

        response = requests.get(self.link, allow_redirects=True)
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
            self.link.replace('list.php', link) for link in all_actual_links
        ]
        path_to_rpd_category = settings.PATH_PDF_RPD / self.identifier
        path_to_rpd_category.mkdir(parents=True, exist_ok=True)
        rpds = []
        for i in range(len(global_all_links)):
            if not global_all_links[i].endswith('.pdf'):
                print(
                    'Ссылка на РПД не содержит .pdf. '
                    f'{global_all_links[i]}',
                )
                continue

            path_to_rpd_file = path_to_rpd_category / all_actual_links[i]
            try:
                response_file = requests.get(global_all_links[i])
                with open(path_to_rpd_file, 'wb') as file:
                    file.write(response_file.content)

                rpds.append(path_to_rpd_file)
            except BaseException as e:
                print(e)

        return rpds


if __name__ == '__main__':
    test_link = (
        'https://www.nntu.ru/sveden/files/rpd/09.04.02/trps_och/list.php'
    )
    parser = OnlineRPDParser('1', test_link)
    # data = parser.get_data()
    # print(data)
