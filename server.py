from aiohttp import web

from main import analyze_urls


async def handle(request):
    urls = request.query.get('urls').split(',')

    if len(urls) >= 10:
        return web.json_response(
            {"error": "too many urls in request, should be 10 or less"},
            status=400
        )

    analuzed_results = await analyze_urls(urls)
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


app = web.Application()
app.add_routes([web.get('/', handle)])


if __name__ == '__main__':
    web.run_app(app)
