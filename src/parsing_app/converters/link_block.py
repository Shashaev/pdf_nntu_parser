import json
import logging
import requests

import transformers

import settings
import schemes


__all__ = []

BASE_PROMPT = '''
Извлеки из текста связи между дисциплинами и классифицируй их по уровням:
- "-1" — школьные дисциплины (младшая, средняя, старшая школа), на которых базируется текущая дисциплина
- "0" — вузовские дисциплины (Не школьные! Программы бакалавриата), на которых базируется текущая дисциплина
- "1" — дисциплины, для которых текущая является основой (пререквизитом)

Текущая дисциплина - <<!base_dis!>>

**Особенности:**
1. Если в тексте нет данных для какой-то группы, оставь список пустым
2. Одна дисциплина не может использоваться несколько раз
3. Названия дисциплин должны точно соответствовать тексту
4. Если рядом с дисциплиной нет слова "школьная" или подобного, то эта дисциплина не относиться к группе -1

Формат вывода (только JSON, без пояснений):
{
'-1': [список школьных дисциплин, которые являются основой для текущей]
'0': [список вузовских дисциплин, которые являются основой для текущей]
'1': [список дисциплин, для которых текущая является основополагающей в изучении]
}

Текст для анализа:

'''


class ExtractiveQA:
    qa_model = transformers.pipeline(
        'question-answering',
        'timpal0l/mdeberta-v3-base-squad2',
        device='cpu',
        low_cpu_mem_usage=True,
    )

    def __init__(self, context: str):
        self.context = context

    def set_context(self, context: str):
        if not context:
            raise ValueError

        self.context = context

    def get_question(self, question: str) -> tuple[str, int]:
        results = self.qa_model(
                    question=question,
                    context=self.context,
                    max_seq_len=512,
                    stride=128,
                    # handle_impossible_answer=True,
                )
        results['answer'] = results['answer'].strip()
        results['answer'] = results['answer'].replace('.', '')
        results['answer'] = results['answer'].replace(';', '')
        results['answer'] = results['answer'].replace('\n', ' ')
        return (results["answer"], results["score"])


class LinkBlock:
    def parsing(self, text) -> list[schemes.LinkRPDScheme]:
        model = ExtractiveQA(text)
        question = 'Какая дисциплина упоминается в тексте?'
        base_dis = model.get_question(question)[0]
        base_dis_norm = (
            base_dis
            .replace('»', '')
            .replace('«', '')
            .strip()
        )
        prompt = {
            "modelUri": f"gpt://{settings.API_CATALOG}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "2000"
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты ассистент, который должен отдавать ответ, только в формате JSON"
                },
                {
                    "role": "user",
                    "text": self.get_prompt(text, base_dis)
                },
            ]
        }
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {settings.API_TOCKEN}"
        }
        response = requests.post(url, headers=headers, json=prompt)
        result = response.json()['result']['alternatives'][0]
        text_result = result['message']['text']
        links: list[schemes.LinkRPDScheme] = []
        try:
            text_result = text_result.replace('\n', '').replace('```', '')
            json_result = json.loads(text_result)
            for link_type in json_result:
                for link_to in json_result[link_type]:
                    try:
                        links.append(
                            schemes.LinkRPDScheme(
                                link_type=int(link_type),
                                link_from=base_dis_norm,
                                link_to=link_to.strip(),
                            )
                        )
                    except Exception as e:
                        logging.error(
                            f'{e}\nОшибка конвертации в pydantic.'
                            f'\nДанные: {json_result[link_type]}'
                        )
        except Exception as e:
            logging.error(
                f'{e}\nДекодируемый текст:\n{text_result}'
            )

        return links

    def is_exists_block(self) -> bool:
        pass

    @staticmethod
    def get_prompt(text: str, base_dis: str) -> str:
        return BASE_PROMPT.replace('<<!base_dis!>>', base_dis) + text

    def __str__():
        return 'LinkBlock'


if __name__ == '__main__':
    text = '''
2. МЕСТО ДИСЦИПЛИНЫ В СТРУКТУРЕ ОБРАЗОВАТЕЛЬНОЙ ПРОГРАММЫ
Учебная дисциплина Б1.В.ОД.8 «Базы данных» включена в перечень обязательных дисци
плин вариативной части (формируемой участниками образовательных отношений), определяющий
направленность ОП. Дисциплина реализуется в соответствии с требованиями ФГОС, ОП ВО и УП.
Дисциплина базируется на дисциплинах программы бакалавриата по направлению «Инфор
матика и вычислительная техника» профиля «Программное обеспечение средств вычислительной
техники и автоматизированных систем». Предшествующими курсами, на которых непосредственно
базируется дисциплина «Базы данных», являются:
«Информатика»;
«Дискретные структуры»;
«Теоретические основы алгоритмизации»;
«Алгоритмы и структуры данных»;
«Программирование».
Дисциплина «Базы данных» является основополагающей для изучения следующих дисци
плин: «Организация и проектирование автоматизированных систем», а также для преддипломной
практики и выполнения ВКР.
'''
    link_parser = LinkBlock()
    links = link_parser.parsing(text)
    logging.info(links)
