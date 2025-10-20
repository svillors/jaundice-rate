import aiohttp
import asyncio
import pymorphy2
from adapters import SANITIZERS

from text_tools import split_by_words, calculate_jaundice_rate


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'https://inosmi.ru/20251020/sholts-275262095.html')
        inosmi_sanitizer = SANITIZERS.get('inosmi_ru')
        text = inosmi_sanitizer(html, plaintext=True)
        morph = pymorphy2.MorphAnalyzer()
        splited_text = split_by_words(morph, text)
        jaundice_rate = calculate_jaundice_rate(splited_text, ['Америка', 'шольц', 'трамп'])
        print(f'Рейтинг: {jaundice_rate}\nСлов в статье: {len(splited_text)}')


asyncio.run(main())
