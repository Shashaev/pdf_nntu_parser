import datetime
import logging
import re

import database.dao as dao
import database.models as models
import logs
import registration


__all__ = []


@registration.run(
    delay_time=7 * 24 * 3600,
    endless_execution=True,
)
@logs.log_start_end
def title_page_ep_conversion():
    ep_dao = dao.EducationalProgramDAO()
    pdfs_ep: list[models.EducationalProgramModel] = ep_dao.select_all()
    description_ep_dao = dao.DescriptionEPDAO()
    description_ep_dao.delete_all()
    for edu_prog in pdfs_ep:
        pdf_ep = ep_dao.get_pdf_by_ep(edu_prog)
        if pdf_ep is None:
            continue

        if 'УЧЕБНЫЙ ПЛАН' not in pdf_ep.text_pdf:
            # logging.error(f'Не распознан титульник: {pdf_ep.path_pdf}')
            continue

        form_education = None
        level = None
        code = None
        name = None
        profile = None
        date_approval = None
        try:
            form_education = get_form_education(pdf_ep.text_pdf)
        except BaseException as e:
            logging.error(
                e,
                f'Путь до проблемного файла: {pdf_ep.path_pdf}',
                exc_info=True,
            )

        try:
            level = get_level(pdf_ep.text_pdf)
        except BaseException as e:
            logging.error(
                e,
                f'Путь до проблемного файла: {pdf_ep.path_pdf}',
                exc_info=True,
            )

        try:
            code = get_code(pdf_ep.text_pdf)
        except BaseException as e:
            logging.error(
                e,
                f'Путь до проблемного файла: {pdf_ep.path_pdf}',
                exc_info=True,
            )

        try:
            name = get_name(pdf_ep.text_pdf)
        except BaseException as e:
            logging.error(
                e,
                f'Путь до проблемного файла: {pdf_ep.path_pdf}',
                exc_info=True,
            )

        try:
            profile = get_profile(pdf_ep.text_pdf)
        except BaseException as e:
            logging.error(
                e,
                f'Путь до проблемного файла: {pdf_ep.path_pdf}',
                exc_info=True,
            )

        try:
            date_approval = get_date_approval(pdf_ep.text_pdf)
        except BaseException as e:
            logging.error(
                e,
                f'Путь до проблемного файла: {pdf_ep.path_pdf}',
                exc_info=True,
            )

        description_ep_dao.create(
            educational_program_id=edu_prog.id_model,
            form_education=form_education,
            level=level,
            code=code,
            name=name,
            profile=profile,
            date_approval=date_approval,
        )


def get_form_education(text_pdf: str) -> models.all_forms_education:
    text_for_search = text_pdf.lower()
    if 'очно-заочная' in text_for_search:
        return 'Очно-заочная'

    if 'заочная' in text_for_search:
        return 'Заочная'

    if 'очная' in text_for_search:
        return 'Очная'

    raise ValueError(
        'Нет ни одной формы обучение: очная, очно-заочная, заочная'
    )


def get_level(text_pdf: str) -> models.all_levels_educational:
    text_for_search = text_pdf.lower()
    if 'аспирант' in text_for_search:
        return 'Аспирантура'

    if 'специалист' in text_for_search:
        return 'Специалитет'

    if 'бакалавр' in text_for_search:
        return 'Бакалавриат'

    if 'магистр' in text_for_search:
        return 'Магистратура'

    raise ValueError(
        'Нет ни одного уровня обучение:'
        ' Специалитет, Бакалавриат, Магистратура, Аспирантура',
    )


def get_code(text_pdf: str) -> str:
    templates = [
        r'\b\d\d.\d\d.\d\d\b',
        r'\b\d.\d\b',
        r'\d\d.\d\d.\d\d',
        r'\d.\d',
    ]
    for template in templates:
        code = re.findall(template, text_pdf)
        if len(code) >= 1:
            return code[0]

    raise ValueError(
        'Кода учебного плана не было найдено в соответствии с шаблонами:'
        f' {templates}',
    )


def get_name(text_pdf: str) -> str:
    taboo_words = [
        'Направление',
        'Специальность',
        'направлению',
        'направление',
        'год',
    ]
    ans: list[str] = re.findall(
        r'(?:Направление|Специальность|направлению)?\s*[:]*\s*\d\d\.\d\d\.\d\d\s*[\-]*\s*\"?[А-Яа-я \-,]+\"?',
        text_pdf,
    )
    for taboo_word in taboo_words:
        ans = [el for el in ans if taboo_word not in el]

    if len(ans) >= 1:
        if len(ans) != 1:
            logging.error(ans)

        new_ans = ans[0].replace('"', '').strip()
        max_digit_ind = -1
        for i in range(len(new_ans)):
            if new_ans[i].isdigit():
                max_digit_ind = i

        new_ans = new_ans[max_digit_ind + 1 :].strip()
        if (
            len(new_ans.split()) == 1
            and new_ans != 'Менеджмент'
            and new_ans != 'Радиотехника'
            and new_ans != 'Машиностроение'
            and new_ans != 'Биотехнология'
            and new_ans != 'Металлургия'
            and new_ans != 'Инноватика'
        ):
            raise ValueError(f'Подозрительное совподение: {ans[0]}')

        for i in range(len(new_ans)):
            if new_ans[i].isalpha():
                break
            elif new_ans[i] == '-':
                new_ans = new_ans[i + 1 :].strip()
                break

        if not new_ans:
            raise ValueError('Специализация не может быть пустой строкой')

        return new_ans

    raise ValueError(
        'Не удалось выявить направление',
    )


def get_profile(text_pdf: str) -> str:
    ans: list[str] = re.findall(
        r'(?:Направленность \(профиль\) подготовки|Направленность \(профиль\)|Направленность \(програма\)|Направленность \(специализация\)|Специализация|Направленность \(программа\)|Направленность  \(cпециализация \)|образовательная программа|направленность)'
        r'\s*[:\-]?\s*\"?[А-Яа-я \-,]+\"?',
        text_pdf,
    )
    prefixes = [
        'Направленность (профиль)',
        'Направленность (программа)',
        'образовательная программа',
        'Направленность (профиль) подготовки',
        'Направленность (специализация)',
        'Направленность (програма)',
        'Специализация',
        'Направленность  (cпециализация )',
        'направленность',
    ]
    to_replace = prefixes + [':', '"']
    taboo_words = ['программа']
    old_ans = ans
    for taboo_word in taboo_words:
        ans = [el for el in ans if taboo_word != el.strip()]

    if len(ans) >= 1:
        if len(ans) != 1:
            logging.error(old_ans, ans)

        new_ans = ans[0]
        for mask in to_replace:
            new_ans = new_ans.replace(mask, ' ')

        new_ans = new_ans.strip()
        if (
            len(new_ans.split()) == 1
            and new_ans != 'Автомобили'
            and new_ans != 'Самолетостроение'
            and new_ans != 'Радиофизика'
        ):
            raise ValueError(
                f'Подозрительное совподение: {new_ans}. '
                f'Исходные найденные подстроки: {old_ans}',
            )

        for i in range(len(new_ans)):
            if new_ans[i].isalpha():
                break
            elif new_ans[i] == '-':
                new_ans = new_ans[i + 1 :].strip()
                break

        if not new_ans:
            raise ValueError('Профиль не может быть пустой строкой')

        return new_ans

    raise ValueError(
        'Не удалось получить профиль',
    )


month_map = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12',
}


def get_date_approval(text_pdf: str) -> str:
    templates = [
        r'Протокол\s*№\s*\d+\s*от\s*\d\d.\d\d.\d\d\d\d',
        r'\d+\s*от\s*\d\d.\d\d.\d\d\d\d',
        r'Протокол\s*№\s*\d+\s*от\s*\"\d{1,2}\"\s*[А-Яа-я]+\s*\d+',
        r'"\d{1,2}\"\s*[А-Яа-я]+\s*\d+',
    ]
    for ind, template in enumerate(templates):
        ans: list[str] = re.findall(template, text_pdf)
        if len(ans) >= 1:
            new_ans = ans[0].replace('"', ' ')
            new_ans = ' '.join(new_ans.split()).strip()
            for month in month_map:
                new_ans = new_ans.replace(month, month_map[month])

            if ind == 2:
                new_ans = new_ans.split('от')[-1].strip()
                return datetime.datetime.strptime(new_ans, '%d %m %Y')
            elif ind == 3:
                return datetime.datetime.strptime(new_ans, '%d %m %Y')
            else:
                new_ans = ''.join(
                    el for el in new_ans.split()[-1] if not el.isalpha()
                )

            return datetime.datetime.strptime(new_ans, '%d.%m.%Y')

    raise ValueError('Не удалось получить дату одобрения')
