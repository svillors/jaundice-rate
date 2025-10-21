import asyncio
from time import monotonic
from enum import Enum

import aiohttp
import anyio
import pymorphy2
from async_timeout import timeout

from adapters import SANITIZERS, ArticleNotFound
from text_tools import split_by_words, calculate_jaundice_rate


TEST_ARTICLES = ['https://inosmi.ru/202123123йцуйцуйцуйцу51013/tomahawk-275135914.html', 'https://inosmi.ru/20251013/gaza-275134570.html', 'https://inosmi.ru/20251020/sholts-275262095.html', 'https://lenta.ru/brief/2021/08/26/afg_terror/']
sanitize = SANITIZERS.get('inosmi_ru')


class ProcessingStatus(Enum):
    OK = 'OK'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'
    TIMEOUT = 'TIMEOUT'


def fetch_charged_words(path, morph):
    with open(path) as f:
        splited_text = split_by_words(morph, f.read())
        return splited_text


async def fetch(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError:
        return


async def process_article(session, morph, charged_words, url, results):
    start = monotonic()
    result = []
    try:
        async with timeout(5):
            html = await fetch(session, url)

            if not html:
                result.extend(
                    [url, None, None, ProcessingStatus.FETCH_ERROR.value])
                return
            try:
                text = sanitize(html, plaintext=True)
                splited_text = split_by_words(morph, text)
                jaundice_rate = calculate_jaundice_rate(
                    splited_text, charged_words)

                result.extend([
                    url, jaundice_rate,
                    len(splited_text), ProcessingStatus.OK.value
                ])
            except ArticleNotFound:
                result.extend(
                    [url, None, None, ProcessingStatus.PARSING_ERROR.value])
    except asyncio.TimeoutError:
        result.extend([url, None, None, ProcessingStatus.TIMEOUT.value])
    finally:
        end = monotonic()
        result.append(end-start)
        results.append(result)


async def main():
    async with aiohttp.ClientSession() as session:
        morph = pymorphy2.MorphAnalyzer()
        charged_words = fetch_charged_words(
            './charged_dict/negative_words.txt', morph)
        results = []

        async with anyio.create_task_group() as tk:
            for url in TEST_ARTICLES:
                tk.start_soon(
                    process_article, session,
                    morph, charged_words,
                    url, results
                )

        for url, rate, count, status, time in results:
            print(f'\nURL: {url}\nСтатус: {status}\n' \
                  f'Рейтинг: {rate}\nКол-во слов: {count}\n' \
                  f'Анализ закончен за {time:.2f} сек.')


if __name__ == "__main__":
    asyncio.run(main())
