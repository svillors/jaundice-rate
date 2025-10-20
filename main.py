import aiohttp
import asyncio
import pymorphy2
from adapters import SANITIZERS

from text_tools import split_by_words, calculate_jaundice_rate


def fetch_charged_words(path, morph):
    with open(path) as f:
        splited_text = split_by_words(morph, f.read())
        return splited_text


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def main():
    async with aiohttp.ClientSession() as session:
        inosmi_sanitizer = SANITIZERS.get('inosmi_ru')
        morph = pymorphy2.MorphAnalyzer()

        html = await fetch(session, 'https://inosmi.ru/20251020/sholts-275262095.html')
        text = inosmi_sanitizer(html, plaintext=True)

        charged_words = fetch_charged_words(
            './charged_dict/negative_words.txt', morph)
        splited_text = split_by_words(morph, text)
        jaundice_rate = calculate_jaundice_rate(splited_text, charged_words)
        print(f'Рейтинг: {jaundice_rate}\nСлов в статье: {len(splited_text)}')


asyncio.run(main())
