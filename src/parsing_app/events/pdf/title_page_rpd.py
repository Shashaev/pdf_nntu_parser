import logging
import re

import tqdm

import registration
import logs
import database.dao as dao
import database.models as models
import schemes


__all__ = []

REJECTED_DISCIPLINES = [
    'КУРСЫ ПО ФИЗИЧЕСКОЙ КУЛЬТУРЕ',
    'ФИЗИЧЕСКАЯ КУЛЬТУРА И СПОРТ',
    'ФИЗИЧЕСКАЯ  КУЛЬТУРА  И СПОРТ',
    'ОСНОВЫ ВОЕННОЙ ПОДГОТОВКИ',
    'ИСТОРИЯ РОССИИ',
    'ОСНОВЫ РОССИЙСКОЙ ГОСУДАРСТВЕННОСТИ',
    '«ИНОСТРАННЫЙ ЯЗЫК»',
    '«ИСТОРИЯ И ФИЛОСОФИЯ НАУКИ»',
    '«ОРГАНИЧЕСКАЯ ХИМИЯ»',
    '«ФИЗИЧЕСКАЯ ХИМИЯ»',
    '«Иностранный язык»',
    '«История и философия науки»',
    '«ВЫЧИСЛИТЕЛЬНАЯ МАТЕМАТИКА»',
    '«МЕХАНИКА ДЕФОРМИРУЕМОГО ТВЕРДОГО ТЕЛА»',
    '«Онтология и теория познания»',
    '«ТЕХНОЛОГИЯ ОРГАНИЧЕСКИХ ВЕЩЕСТВ»',
    '«МЕХАНИКА ЖИДКОСТИ, ГАЗА И ПЛАЗМЫ»',
    '«РЕГИОНАЛЬНАЯ И ОТРАСЛЕВАЯ ЭКОНОМИКА»',
    '«ПРОЦЕССЫ И АППАРАТЫ ХИМИЧЕСКИХ ТЕХНОЛОГИЙ»',
    '«ОБРАБОТКА МЕТАЛЛОВ ДАВЛЕНИЕМ»',
    '«ПРОЕКТИРОВАНИЕ И КОНСТРУКЦИЯ СУДОВ»',
    'Объектно-ориентированное проектирование автоматизированных систем',
    'Объектно -ориентированное проектирование автоматизированных систем',
    'Основы информационных систем',
    '«МАТЕМАТИЧЕСКОЕ МОДЕЛИРОВАНИЕ, ЧИСЛЕННЫЕ МЕТОДЫ',
    '«АВТОМАТИЗАЦИЯ И УПРАВЛЕНИЕ ТЕХНОЛОГИЧЕСКИМИ ПРОЦЕССАМИ',
    '«СИСТЕМНЫЙ АНАЛИЗ, УПРАВЛЕНИЕ И ОБРАБОТКА ИНФОРМАЦИИ',
    '«РАДИОЛОКАЦИЯ И РАДИОНАВИГАЦИЯ»',
    '«АНТЕННЫ, СВЧ-УСТРОЙСТВА И ИХ ТЕХНОЛОГИИ»',
    '«МЕТОДЫ И ПРИБОРЫ КОНТРОЛЯ И ДИАГНОСТИКИ МАТЕРИАЛОВ',
    '«ТЕХНОЛОГИЯ И ОБОРУДОВАНИЕ ДЛЯ ПРОИЗВОДСТВА МАТЕРИАЛОВ',
    '«ЭЛЕКТРОХИМИЯ»',
    '«ОТЕЧЕСТВЕННАЯ ИСТОРИЯ»',
    '«ПРОЦЕССЫ И АППАРАТЫ ХИМИЧЕСКИХ ТЕХНОЛОГИЙ»',
    '«ТЕХНОЛОГИЯ ОРГАНИЧЕСКИХ ВЕЩЕСТВ»',
    '«ТЕХНОЛОГИЯ ЭЛЕКТРОХИМИЧЕСКИХ ПРОЦЕССОВ И ЗАЩИТА',
    '«ЛИТЕЙНОЕ ПРОИЗВОДСТВО»',
    '«ПРОЕКТИРОВАНИЕ И КОНСТРУКЦИЯ СУДОВ»',
    '«ТЕОРИЯ КОРАБЛЯ И СТРОИТЕЛЬНАЯ МЕХАНИКА»',
    '«НАЗЕМНЫЕ ТРАНСПОРТНО-ТЕХНОЛОГИЧЕСКИЕ',
    '«ТЕХНОЛОГИЯ МАШИНОСТРОЕНИЯ»',
    '«МЕТАЛЛОВЕДЕНИЕ И ТЕРМИЧЕСКАЯ ОБРАБОТКА МЕТАЛЛОВ И СПЛАВОВ»',
    '«ИНЖЕНЕРНАЯ ГЕОМЕТРИЯ И КОМПЬЮТЕРНАЯ ГРАФИКА',
    '«ЯДЕРНЫЕ ЭНЕРГЕТИЧЕСКИЕ УСТАНОВКИ, ТОПЛИВНЫЙ ЦИКЛ',
    'СТРОИТЕЛЬНАЯ МЕХАНИКА МАШИН',
    '«СУДОВЫЕ ЭНЕРГЕТИЧЕСКИЕ УСТАНОВКИ И ИХ ЭЛЕМЕНТЫ',
    '«ТУРБОМАШИНЫ И ПОРШНЕВЫЕ ДВИГАТЕЛИ»',
    '«ЭНЕРГЕТИЧЕСКИЕ СИСТЕМЫ И КОМПЛЕКСЫ»',
    '«ЭЛЕКТРОТЕХНИЧЕСКИЕ КОМПЛЕКСЫ И СИСТЕМЫ»',
    '«КОМПЬЮТЕРНОЕ МОДЕЛИРОВАНИЕ И АВТОМАТИЗАЦИЯ',
    '«УПРАВЛЕНИЕ В ОРГАНИЗАЦИОННЫХ СИСТЕМАХ»',
    '«СИСТЕМЫ, СЕТИ И УСТРОЙСТВА ТЕЛЕКОММУНИКАЦИЙ»',
    '«ЭЛЕКТРОЭНЕРГЕТИКА»',
    '«ИНФОРМАТИКА И ИНФОРМАЦИОННЫЕ ПРОЦЕССЫ»',
    '«РАДИОТЕХНИКА, В ТОМ ЧИСЛЕ СИСТЕМЫ И УСТРОЙСТВА ТЕЛЕВИДЕНИЯ»',
    '«РАДИОФИЗИКА»',
    '«СОПРОТИВЛЕНИЕ МАТЕРИАЛОВ»',
]
ENDS_TITLE_PAGE = [
    r'[Нн] *[Ии] *[Жж] *[Нн] *[Ии] *[Йй]\s*'
    r'[Нн] *[Оо] *[Вв] *[Гг] *[Оо] *[Рр] *[Оо] *[Дд]',
    r'[Рр]\s*[Аа]\s*[Зз]\s*[Рр]\s*[Аа]\s*[Бб]\s*[Оо]\s*[Тт]\s*[Чч]\s*[Ии]\s*[Кк]',
    r'\([Пп]\s*[Оо]\s*[Дд]\s*[Пп]\s*[Ии]\s*[Сс]\s*[Ьь]\)',
]
START_CONTENT = [
    'СОДЕРЖАНИЕ',
    'Оглавление',
    'ОГЛАВЛЕНИЕ',
]
MAXIMUM_NUMBER_ERRORS = float('inf')


@registration.run(
    delay_time=7 * 24 * 3600,
    endless_execution=True,
)
@logs.log_start_end
def title_page_ep_conversion():
    rpd_dao = dao.RPDDAO()
    description_rpd_dao = dao.DescriptionRPDDAO()
    description_rpd_dao.delete_all()
    rpds: list[models.RPDModel] = rpd_dao.select_all()
    number_errors = 0
    for rpd in tqdm.tqdm(rpds):
        if number_errors >= MAXIMUM_NUMBER_ERRORS:
            logging.error(
                f'Кол-во ошибок превзошло максимум ({MAXIMUM_NUMBER_ERRORS = }), '
                'поэтому дальнейшая обработка rpd останавливается. '
                'Если вам нужно продолжить вне зависимости '
                'от эти факторов, то увеличте константу MAXIMUM_NUMBER_ERRORS.'
            )
            break

        pdf_rpd = rpd_dao.get_pdf_by_rpd(rpd)
        text_pdf = pdf_rpd.text_pdf
        for word_content in START_CONTENT:
            if word_content in text_pdf:
                text_pdf = text_pdf.split(word_content, 1)[0]

        re_ans = re.findall(
            r'лист\s*актуализации',
            text_pdf.lower(),
        )
        if len(re_ans) >= 1:
            logging.debug(
                f'Лист актуализации рабочей программы дисциплины (ключ выявления - {re_ans}): '
                f'{pdf_rpd.path_pdf}',
            )
            continue

        re_ans = re.findall(
            r'[Дд]ополнения\s*и\s*изменения\s*к\s*рабочей\s*программ\s*е\s*дисциплины',
            text_pdf.lower(),
        )
        if len(re_ans) >= 1:
            logging.debug(
                f'Лист дополнений и изменений (ключ выявления - {re_ans}): '
                f'{pdf_rpd.path_pdf}',
            )
            continue

        is_continue = False
        text_for_check = text_pdf.replace(' ', '').lower()
        for rejected_discipline in REJECTED_DISCIPLINES:
            if rejected_discipline.replace(' ', '').lower() in text_for_check:
                is_continue = True
                break

        if is_continue:
            continue

        text_title_page = None
        for end_title_page in ENDS_TITLE_PAGE:
            re_find = re.findall(end_title_page, text_pdf)
            if not re_find:
                continue

            text_title_page = re.split(
                end_title_page,
                text_pdf,
                1,
            )[0]
            logging.debug(f'Используемый разделитель: {end_title_page}')
            break

        if text_title_page is None:
            number_errors += 1
            logging.info(
                'Титульник не распознан или неожиданный конец титульника. '
                f'Начало текста для поиска титульника: {repr(text_pdf[:50])}. \n'
                f'Конец: {repr(text_pdf[-50:])}.\n'
                f'Путь до файла: {pdf_rpd.path_pdf.replace('\\', '\\\\')}',
            )
            continue

        if len(text_title_page) <= 100:
            logging.info(
                'Подозрительно слишком малая длина титульника. Выявленный титульник:\n '
                f'{text_pdf}.\n'
                f'Путь до файла: {pdf_rpd.path_pdf.replace('\\', '\\\\')}',
            )
            continue

        try:
            index = get_index(text_title_page)
        except NameError as e:
            logging.debug(
                f'{e}\nПуть до файла: {pdf_rpd.path_pdf}',
            )
        except BaseException as e:
            number_errors += 1
            logging.error(
                f'{e}\nПуть до проблемного файла: {pdf_rpd.path_pdf}',
            )
            continue

        try:
            description_rpd = schemes.DescriptionRPDScheme(
                index=index,
            )
        except BaseException as e:
            logging.error(
                'Ошибка при приведении типов в pydantic '
                f'{index = }:\n{e}',
            )

        try:
            description_rpd_dao.create(rpd=rpd, **description_rpd.model_dump())
        except BaseException as e:
            logging.error(
                f'Ошибка при записи данных в БД ({description_rpd}):\n{e}'
            )


patterns = [
    r'Б *\d *\. *Б *\. *\d *\. *\d *\. *\d+',
    r'Б *\d *\. *Б *\. *О *Д *\. *\d+',
    r'Б *\d *\. *Б *\.? *\d+',
    r'Б *\d *\. *[ВB] *\. *Д *\.? *[ВB] *\.? *\d\ *. *\d+',
    r'Б *\d *\. *В *\. *Д *\.? *\d *\. *\d *\. *\d+',
    r'Б *\d *\. *В *\. *Д *В *\. *Д *\. *\d',
    r'Б *\d *\. *В *\. *Д *О *\. *\d+',
    r'Б *\d *\. *В *\. *В *Д *\. *\d *\. *\d+',
    r'Б *\d *\. *В *\. *В *Д *\. *\d *\. *\d+',
    r'Б *\d *\. *В *\.? *Д *В *\.? *\d+',
    r'Б *\d *\. *В *\d *\. *Д *В *\. *\d *\. *\d+',
    r'Б *\d *\. *О *\. *\d+',
    r'Б *\d *\. *\d+ *\. *\d+',
    r'Б *\d *\. *И *\. *О *Д *\. *\d+',
    r'Б *\d *\.? *Б *\. *\d+',
    r'Б *\d *\.? *В *\. *О *Д *\.? *\d+',
    r'Б *\d? *\. *\d *\.? *В *\. *Д *В *\.? *\d\. *\d+',
    r'Б *\d? *\. *\d? *Б *\.? *\d+',
    r'Б *\d? *\. *[ВB] *\. *[ОO] *Д *\. *\d+',
    r'Б *\. *\d *\. *Б *\. *\d *\. *\d *\.? *\d+',
    r'Б *\. *\d *\. *Б *\. *\d+',
    r'Б *\. *\d *\. *Б *\d+',
    r'Б *\. *\d *\.? *В *\. *О *Д *\. *\d+',
    r'[МM] *\d *\. *Б *\.? *\d+',
    r'[МM] *\d *\. *В *\. *О *Д *\. *\d+',
    r'[МM] *\d *\. *В *\. *Д *В *\. *\d *\. *\d',
    r'Ф *\.? *Т *Д *\. *\d+',
    r'Ф *Д *Т *\. *\d+',
]
for i in range(len(patterns)):
    patterns[i] = re.compile(patterns[i])


def get_index(text_pdf: str) -> str:
    text_pdf = text_pdf.replace(',', '.')
    all_occurrences_found = []
    for pattern in patterns:
        ans: list[str] = pattern.findall(text_pdf)
        all_occurrences_found.extend(ans)
        for i in range(len(ans)):
            ans[i] = ans[i].strip().replace(' ', '')

        if not ans:
            continue

        if len(set(ans)) >= 2:
            raise NameError(
                f'Кол-во индексов на титульном листе >= 2 ({list(set(ans))}). '
                'Возмжоно не правильное определение титульного листа. '
                'Начало текста, в котором происходит '
                f'поиск:\n {repr(text_pdf[:50])}.\n'
                f'Конец текста:\n {repr(text_pdf[-50:])}',
            )

        ans: str = ans[0]
        for par in ('MМ', 'BВ', 'OО'):
            ans = ans.replace(par[0], par[1])

        if 'ДВ' in ans and ans[ans.rindex('В') + 1] not in ' .':
            ind_s = ans.rindex('В') + 1
            ans = f'{ans[:ind_s]}.{ans[ind_s:]}'

        return ans

    raise ValueError(
        'Индекс РПД не найден. Найденные вхождение, '
        'которые не были распознаны как индекс: '
        f'{all_occurrences_found}. Начала текста для '
        f'поиска: {text_pdf[:50]}. Конец: {text_pdf[-50:]}.'
    )
