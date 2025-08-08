import re
import logging

import tqdm

import registration
import logs
import database.dao as dao
import database.models as models


__all__ = []

BEGINNING_SECTION_LINK_BLOCK = [
    r'[12]?[\s-]*\.?[\s-]*М[\s-]*Е[\s-]*С[\s-]*Т[\s-]*О[\s-]*'
    r'Д[\s-]*И[\s-]*С[\s-]*Ц[\s-]*И[\s-]*3?[\s-]*П[\s-]*Л[\s-]*И[\s-]*Н[\s-]*Ы?[\s\S]*[\s-]*'
    r'В[\s-]*С[\s-]*Т[\s-]*Р[\s-]*У[\s-]*К[\s-]*Т[\s-]*У[\s-]*'
    r'Р[\s-]*Е[\s-]*О[\s-]*Б[\s-]*Р[\s-]*А[\s-]*З[\s-]*О[\s-]*В'
    r'[\s-]*А[\s-]*Т[\s-]*Е[\s-]*Л[\s-]*Ь[\s-]*Н[\s-]*О[\s-]*Й'
    r'[\s-]*П[\s-]*Р[\s-]*О[\s-]*Г[\s-]*Р[\s-]*А?[\s-]*М[\s-]*М[\s-]*Ы',
]
BEGINNING_SECTION_PURPOSE_BLOCK = [
    r'1?[\s-]*\.?[\s-]*Ц[\s-]*Е[\s-]*Л[\s-]*И[\s-]*И[\s-]*З[\s-]*'
    r'А[\s-]*Д[\s-]*А[\s-]*Ч[\s-]*И[\s-]*'
    r'О[\s-]*С[\s-]*В[\s-]*О[\s-]*Е[\s-]*Н[\s-]*И[\s-]*Я[\s-]*'
    r'Д[\s-]*И[\s-]*С[\s-]*Ц[\s-]*И[\s-]*П[\s-]*Л[\s-]*И[\s-]*Н[\s-]*Ы'
    r'[\s-]*\([\s-]*М[\s-]*О[\s-]*Д[\s-]*У[\s-]*Л[\s-]*Я[\s-]*\)',
    r'1?[\s-]*\.?[\s-]*Ц[\s-]*Е[\s-]*Л[\s-]*[ИЬ][\s-]*И[\s-]*З[\s-]*'
    r'А[\s-]*Д[\s-]*А[\s-]*Ч[\s-]*И'
    r'[\s-]*О[\s-]*С[\s-]*В[\s-]*О[\s-]*Е[\s-]*Н[\s-]*И[\s-]*Я[\s-]*'
    r'Д[\s-]*И[\s-]*С[\s-]*Ц[\s-]*И[\s-]*П[\s-]*Л[\s-]*И[\s-]*Н[\s-]*Ы',
    r'1[\s-]*\.[\s-]*П[\s-]*Л[\s-]*А[\s-]*Н[\s-]*И[\s-]*Р[\s-]*У[\s-]*Е[\s-]*М[\s-]*Ы[\s-]*Е[\s-]*'
    r'[\s-]*Р[\s-]*Е[\s-]*З[\s-]*У[\s-]*Л[\s-]*Ь[\s-]*Т[\s-]*А[\s-]*Т[\s-]*Ы[\s-]*'
    r'[\s-]*О[\s-]*Б[\s-]*У[\s-]*Ч[\s-]*Е[\s-]*Н[\s-]*И[\s-]*Я[\s-]*'
    r'П[\s-]*О[\s-]*Д[\s-]*И[\s-]*С[\s-]*Ц[\s-]*И[\s-]*П[\s-]*Л[\s-]*И[\s-]*Н[\s-]*Е'
    r'[\s-]*\([\s-]*М[\s-]*О[\s-]*Д[\s-]*У[\s-]*Л[\s-]*Ю[\s-]*\)[\s-]*,[\s-]*'
    r'[\s-]*С[\s-]*О[\s-]*О[\s-]*Т[\s-]*Н[\s-]*Е[\s-]*С[\s-]*Е[\s-]*Н[\s-]*Н[\s-]*Ы[\s-]*Е'
    r'[\s-]*С[\s-]*П[\s-]*Л[\s-]*А[\s-]*Н[\s-]*И[\s-]*Р[\s-]*У[\s-]*Е[\s-]*М[\s-]*Ы[\s-]*М[\s-]*И'
    r'[\s-]*Р[\s-]*Е[\s-]*З[\s-]*У[\s-]*Л[\s-]*Ь[\s-]*Т[\s-]*А[\s-]*Т[\s-]*А[\s-]*М[\s-]*И'
    r'[\s-]*О[\s-]*С[\s-]*В[\s-]*О[\s-]*Е[\s-]*Н[\s-]*И[\s-]*Я'
    r'[\s-]*О[\s-]*Б[\s-]*Р[\s-]*А[\s-]*З[\s-]*О[\s-]*В[\s-]*А[\s-]*'
    r'[\s-]*Т[\s-]*Е[\s-]*Л[\s-]*Ь[\s-]*Н[\s-]*О[\s-]*Й[\s-]*'
    r'П[\s-]*Р[\s-]*О[\s-]*Г[\s-]*Р[\s-]*А[\s-]*М[\s-]*М[\s-]*Ы',
    r'Ц[\s-]*Е[\s-]*Л[\s-]*И[\s-]*'
    r'И[\s-]*З[\s-]*А[\s-]*Д[\s-]*А[\s-]*Ч[\s-]*И[\s-]*'
    r'Е[\s-]*Е[\s-]*О[\s-]*С[\s-]*В[\s-]*О[\s-]*Е[\s-]*Н[\s-]*И[\s-]*Я'
]
BEGINNING_SECTION_COMPETENCE_BLOCK = [
    r'3?[\s-]*\.?[\s-]*К[\s-]*О[\s-]*М[\s-]*П[\s-]*Е[\s-]*Т[\s-]*Е[\s-]*Н[\s-]*Ц[\s-]*И[\s-]*И'
    r'[\s-]*О[\s-]*Б[\s-]*У[\s-]*Ч[\s-]*А[\s-]*Ю[\s-]*Щ[\s-]*Е[\s-]*Г[\s-]*О[\s-]*С[\s-]*Я'
    r'[\s-]*,[\s-]*Ф[\s-]*О[\s-]*Р[\s-]*М[\s-]*И[\s-]*Р[\s-]*У[\s-]*Е[\s-]*М[\s-]*Ы[\s-]*Е'
    r'[\s-]*В[\s-]*Р[\s-]*Е[\s-]*З[\s-]*У[\s-]*Л[\s-]*Ь[\s-]*Т[\s-]*А[\s-]*Т[\s-]*Е'
    r'[\s-]*О[\s-]*С[\s-]*В[\s-]*О[\s-]*Е[\s-]*Н[\s-]*И[\s-]*Я'
    r'[\s-]*Д[\s-]*И[\s-]*С[\s-]*Ц[\s-]*И[\s-]*П[\s-]*Л[\s-]*И[\s-]*Н[\s-]*Ы?',
    r'3?[\s-]*\.?[\s-]*П[\s-]*Е[\s-]*Р[\s-]*Е[\s-]*Ч[\s-]*Е[\s-]*Н[\s-]*Ь'
    r'[\s-]*П[\s-]*Л[\s-]*А[\s-]*Н[\s-]*И[\s-]*Р[\s-]*У[\s-]*Е[\s-]*М[\s-]*Ы[\s-]*Х'
    r'[\s-]*Р[\s-]*Е[\s-]*З[\s-]*У[\s-]*Л[\s-]*Ь[\s-]*Т[\s-]*А[\s-]*Т[\s-]*О[\s-]*В'
    r'[\s-]*О[\s-]*Б[\s-]*У[\s-]*Ч[\s-]*Е[\s-]*Н[\s-]*И[\s-]*Я'
    r'[\s-]*П[\s-]*О'
    r'[\s-]*Д[\s-]*И[\s-]*С[\s-]*Ц[\s-]*И[\s-]*П[\s-]*Л[\s-]*И[\s-]*Н[\s-]*Е',
    r'3[\s-]*\.[\s-]*О[\s-]*Б[\s-]*Ъ[\s-]*Е[\s-]*М'
    r'[\s-]*Д[\s-]*И[\s-]*С[\s-]*Ц[\s-]*И[\s-]*П[\s-]*Л[\s-]*И[\s-]*Н[\s-]*Ы'
]


@registration.run(
    delay_time=7 * 24 * 3600,
    endless_execution=True,
)
@logs.log_start_end
def get_text_link_blocks():
    text_link_block_dao = dao.TextLinkBlockDAO()
    rpd_dao = dao.RPDDAO()
    text_link_block_dao.delete_all()
    all_rpd = rpd_dao.select_all()
    for rpd in tqdm.tqdm(all_rpd):
        rpd_pdf = rpd_dao.get_pdf_by_rpd(rpd)
        if is_list_actual(rpd_pdf):
            logging.debug(
                f'Встретился лист актулизации.\nПуть до файла: {rpd_pdf.path_pdf}'
            )
            continue

        text_pdf = rpd_pdf.text_pdf
        text_pdf = ' '.join(re.split(r' +', text_pdf))
        for par in ('MМ', 'BВ', 'OО', 'EЕ'):
            text_pdf = text_pdf.replace(par[0], par[1])
            text_pdf = text_pdf.replace(par[0].lower(), par[1].lower())

        try:
            text_link_block = get_text_link_block(text_pdf)
        except Exception as e:
            logging.error(
                f'{e}\nПуть до файла: {rpd_pdf.path_pdf}'
                f'\nПуть до файла с экранированием \\: '
                f'{rpd_pdf.path_pdf.replace("\\", "\\\\")}'
            )
            continue

        try:
            text_link_block_dao.create(
                rpd=rpd,
                text=text_link_block,
            )
        except Exception as e:
            logging.error(
                f'{e}\nОшибка при сохранении текста: {text_link_block}'
            )


def get_text_link_block(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError(f'Тип переданного значение не str ({text = })')

    f = True
    for beginning in BEGINNING_SECTION_PURPOSE_BLOCK:
        matches = re.findall(beginning, text, re.IGNORECASE)
        if matches:
            text = text.split(matches[-1])[-1]
            f = False

    if f:
        raise ValueError(
            'В файле не найден раздел '
            '"1. ЦЕЛИ И ЗАДАЧИ ОСВОЕНИЯ ДИСЦИПЛИНЫ (МОДУЛЯ)".'
        )

    texts_link_block = []
    for beginning in BEGINNING_SECTION_LINK_BLOCK:
        matches = re.findall(beginning, text, re.IGNORECASE)
        if 1 <= len(matches) <= 2:
            texts_link_block.append(
                matches[0]
                + text.split(matches[0], 1)[1]
            )
        elif len(matches) > 2:
            raise ValueError(
                'В тексте найдёно несколько началов раздела. '
                f'Список найдённых расделов = {matches}.'
            )

    if len(texts_link_block) == 0:
        raise ValueError(
            'В файле не найден искомый раздел. '
            f'Начало поиска:\n{repr(text[:50])}\nКонец текста:\n'
            f'{repr(text[-50:])}'
        )
    elif len(texts_link_block) > 1:
        raise ValueError(
            'В тексте найдёно несколько началов раздела. '
            f'Список найдённых расделов = {texts_link_block}.'
        )

    text_list_block = texts_link_block[0]
    f = True
    for beginning in BEGINNING_SECTION_COMPETENCE_BLOCK:
        matches = re.findall(beginning, text_list_block, re.IGNORECASE)
        for template in matches:
            f = False
            text_list_block = text_list_block.split(
                template,
                1,
            )[0]

    if f:
        raise ValueError(
            'В файле не найден следующий раздел после искомого. '
            f'Начало поиска:\n{repr(text[:50])}\nКонец текста:\n'
            f'{repr(text[-50:])}'
        )
    elif len(text_list_block) <= 10:
        raise ValueError(
            'Найденный текст блока связей подозрительно малый:\n'
            f'{text_list_block}'
        )

    return text_list_block


KEYS_RELEVANCE_SHEET = [
    r'List_aktual',
    r'List_katual',
]


def is_list_actual(pdf: models.PDFRPDModel) -> bool:
    for template in KEYS_RELEVANCE_SHEET:
        matches = re.findall(template, pdf.path_pdf, re.IGNORECASE)
        if matches:
            return True

    return False
