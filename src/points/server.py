from aiohttp import web

from src.points.wire.websocket import websocket_handler


def websocket_server():
    app = web.Application()
    app.router.add_get("/", websocket_handler)
    return app
