import asyncio
import uuid

import aiohttp
import orjson
from aiohttp import web
from loguru import logger

from src.points.connections import BroadcastManager
from src.points.service import handle

manager = BroadcastManager()


async def websocket_handler(request):

    ws = web.WebSocketResponse()
    logger.info(f"incoming connection")
    await ws.prepare(request)
    client_id = uuid.uuid4()
    manager.add_client(client_id, ws)
    await asyncio.create_task(handle_message(ws, client_id))
    return ws


async def handle_message(ws, client_id):
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                message = parse(msg.data)
                await handle(message, client_id)
            else:
                # do something
                pass
    finally:
        await manager.remove_client(client_id)


def parse(msg):
    # validate
    return orjson.loads(msg)
