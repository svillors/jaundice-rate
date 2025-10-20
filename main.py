import aiohttp
import asyncio
import anyio
import pymorphy2
from adapters import SANITIZERS

from text_tools import split_by_words, calculate_jaundice_rate


TEST_ARTICLES = ['https://inosmi.ru/20251013/tomahawk-275135914.html', 'https://inosmi.ru/20251013/gaza-275134570.html', 'https://inosmi.ru/20251020/sholts-275262095.html']
sanitize = SANITIZERS.get('inosmi_ru')


def fetch_charged_words(path, morph):
    with open(path) as f:
        splited_text = split_by_words(morph, f.read())
        return splited_text


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def process_article(session, morph, charged_words, url, results):
    html = await fetch(session, url)
    text = sanitize(html, plaintext=True)
    splited_text = split_by_words(morph, text)
    jaundice_rate = calculate_jaundice_rate(splited_text, charged_words)

    results.append((url, jaundice_rate, len(splited_text)))


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

        for url, rate, count in results:
            print(f'URL: {url}\nРейтинг: {rate}\nКол-во слов: {count}\n')


if __name__ == "__main__":
    asyncio.run(main())
