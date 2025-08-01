import functools
import logging

import numpy as np
import pandas as pd
import tabula

import converters.base_converter as base_converter
import database.models as models
import schemes


__all__ = []


class DisciplineTable(base_converter.BlockParser):
    key_work = {
        'Экзамены': 'format_control_exam',
        'Зачеты': 'format_control_test',
        'Зачетысоценкой': 'format_control_assessment_test',
        'Курсовыепроекты': 'format_control_course_project',
        'Курсовыеработы': 'format_control_course_work',
        'Контрольные': 'format_control_control',
        'Рефераты': 'format_control_essay',
        'РГР': 'format_control_rgr',
    }

    def __init__(self, pdf: models.PDFEducationalProgramModel):
        super().__init__(pdf)
        self.count = 0
        self.name_columns = []

    @staticmethod
    def clear_baz_var(table: pd.DataFrame) -> pd.DataFrame:
        mask = table.eq('Баз').any(axis=1)
        table = table.drop(table[mask].index)
        mask = table.eq('Вар').any(axis=1)
        return table.drop(table[mask].index)

    @staticmethod
    def get_first_non_empty_columns(
        table: pd.DataFrame,
        count: int,
    ) -> list[str]:
        target_columns = []
        ind = 0
        while ind < len(table.columns) and len(target_columns) < count:
            name_column = table.columns[ind]
            max_num = 0
            for i in range(len(table[name_column])):
                try:
                    value = int(float(table[name_column].iloc[i]))
                    max_num = max(max_num, value)
                except BaseException:
                    pass

            if (max_num >= 100 or max_num == 72) and table[
                name_column
            ].count() == len(table[name_column]):
                break

            if table[name_column].count() != 0:
                target_columns.append(name_column)

            ind += 1

        for i in range(len(target_columns), count):
            name_new_column = f'Fake_column_{i}'
            table[name_new_column] = np.nan
            target_columns.append(name_new_column)

        return target_columns

    @staticmethod
    def get_last_non_empty_columns(
        table: pd.DataFrame,
        count: int,
    ) -> list[str]:
        target_columns = []
        ind = len(table.columns) - 1
        while len(target_columns) < count:
            name_column = table.columns[ind]
            if table[name_column].count() != 0:
                target_columns.append(name_column)

            ind -= 1

        return target_columns

    def parsing(self) -> list[schemes.RowDisciplineTableScheme]:
        pdf: models.PDFEducationalProgramModel = self.pdf
        pdf_file = tabula.read_pdf(
            pdf.path_pdf,
            pages='all',
            multiple_tables=True,
        )
        for ind in range(len(pdf_file)):
            if 'Индекс' in pdf_file[ind].columns:
                break

        table1 = pdf_file[ind][3:]
        if (ind + 1) >= len(pdf_file):
            print(f'{ind+1=}: {len(pdf_file)=}: {self.pdf.absolute()}')

        table2 = pdf_file[ind + 1]
        new_row = list(table2.columns)
        for i in range(len(new_row)):
            if new_row[i].startswith('Unnamed:'):
                new_row[i] = np.nan

            try:
                new_row[i] = int(float(new_row[i]))
            except BaseException:
                pass

        table2.loc[len(table2)] = new_row
        tables = [table1, table2]
        for i in range(len(tables)):
            tables[i] = self.clear_baz_var(tables[i])
            tables[i] = tables[i].dropna(subset=[tables[i].columns[0]])
            target_columns = self.get_first_non_empty_columns(
                tables[i],
                2 + self.count,
            ) + self.get_last_non_empty_columns(tables[i], 1)
            tables[i] = tables[i][target_columns]
            tables[i] = tables[i].rename(
                columns={
                    tables[i].columns[j]: self.name_columns[j]
                    for j in range(len(self.name_columns))
                },
            )

        table = pd.concat(tables, ignore_index=True)
        table = table.drop_duplicates()
        data = table.to_dict()
        all_len = len(data['index'])
        for key in data:
            if len(data[key]) != all_len:
                logging.error(
                    f'Кол-во строк в столбце index = {all_len}, '
                    f'но столбце {key} = {len(data[key])}',
                    data,
                )
                raise ValueError(
                    'Количество строк не совпадает в разных столбцах',
                )

        list_row = []
        for i in data['index']:
            row = {}
            for key in data:
                if i not in data[key]:
                    raise ValueError(
                        f'Нет подходящего индекса: запрашивается {i}, но элемент = {data[key]}',
                    )

                row[key] = data[key][i]

            for key in row:
                value = row[key]
                if isinstance(value, str):
                    pass
                elif np.isnan(value):
                    value = None
                elif (
                    isinstance(value, (int, float))
                    and value != float('inf')
                    and value != float('nan')
                ):
                    value = str(int(float(value)))
                else:
                    raise ValueError(
                        f'Недопустимый тип элемента: type({value}) = {type(value)}',
                    )

                if key in ['index', 'name', 'code'] and value is None:
                    logging.info(
                        f'Пусто значение {key}: {row}. Файл: {pdf.path_pdf}',
                    )
                    break

                row[key] = value
            else:
                try:
                    list_row.append(schemes.RowDisciplineTableScheme(**row))
                except BaseException as e:
                    logging.error(e, row)

        return list_row

    @functools.lru_cache
    def is_exists_block(self) -> bool:
        pdf: models.PDFEducationalProgramModel = self.pdf
        text_pdf = pdf.text_pdf.replace('\n', '').replace(' ', '')
        self.name_columns = [
            'index',
            'name',
        ]
        for el in self.key_work:
            if el in text_pdf:
                self.count += 1
                self.name_columns.append(self.key_work[el])

        self.name_columns.append('code')
        return (
            'УЧЕБНЫЙПЛАН' in text_pdf
            and '2.Сводныеданные' in text_pdf
            and 'Наименование' in text_pdf
            and 'Индекс' in text_pdf
            and 'Код' in text_pdf
            and 'Формыконтроля' in text_pdf
        )

    def __str__():
        return 'SummaryDataTable'
