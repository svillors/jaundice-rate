from aiohttp import web


async def handle(request):
    urls = request.query.get('urls').split(',')
    response = {'urls': urls}
    return web.json_response(response)


app = web.Application()
app.add_routes([web.get('/', handle)])


if __name__ == '__main__':
    web.run_app(app)
