from aiohttp import web

from main import analyze_urls


async def handle(request):
    urls = request.query.get('urls').split(',')
    analuzed_results = await analyze_urls(urls)
    return web.json_response(analuzed_results)


app = web.Application()
app.add_routes([web.get('/', handle)])


if __name__ == '__main__':
    web.run_app(app)
