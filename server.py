import pymorphy2
from aiohttp import web

from main import analyze_urls


async def handle(request):
    morph = request.app.get('morph')
    urls = request.query.get('urls').split(',')

    if len(urls) >= 10:
        return web.json_response(
            {"error": "too many urls in request, should be 10 or less"},
            status=400
        )

    analuzed_results = await analyze_urls(urls, morph)
    response = []

    for url, rate, count, status, time in analuzed_results:
        result = {}
        result['status'] = status
        result['url'] = url
        result['score'] = rate
        result['words_count'] = count
        result['analyze_time'] = time
        response.append(result)

    return web.json_response(response)


if __name__ == '__main__':
    app = web.Application()
    app['morph'] = pymorphy2.MorphAnalyzer()
    app.add_routes([web.get('/', handle)])
    web.run_app(app)
