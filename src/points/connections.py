import asyncio
import uuid
from collections import defaultdict

import orjson
from aiohttp import web
from loguru import logger

from src.points import repository
from src.points.utils import parse_points


class BroadcastManager:
    _instance = None
    _subscribers_by_id: dict[uuid.UUID, int] = {}
    _subscribers_by_symbol: dict[int, set[uuid.UUID]] = defaultdict(set)
    _connected_clients: dict[uuid.UUID, web.WebSocketResponse] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BroadcastManager, cls).__new__(cls)
            cls._instance._connected_clients = {}
        return cls._instance

    def add_client(self, client_id: uuid.UUID, ws: web.WebSocketResponse):
        self._connected_clients[client_id] = ws

    async def remove_client(self, client_id: uuid.UUID):
        self.unsubscribe(client_id)
        ws: web.WebSocketResponse = self._connected_clients.pop(client_id)
        try:
            await ws.close()
        finally:
            logger.info("connect [some_connect_id] is closed")

    async def send_history(self, client_id: uuid.UUID, symbol_id: int) -> None:
        history_data = await repository.get_history(symbol_id)
        history_points = await parse_points(history_data)
        message = {"action": "asset_history", "message": {"points": history_points}}
        await self.send_message(client_id, message)

    async def broadcast(self, stop_event: asyncio.Event, points_queues: dict[int, asyncio.Queue]):
        while not stop_event.is_set():
            for asset_id, queue in points_queues.items():  # type: int, asyncio.Queue
                point: dict = await queue.get()
                subscribers: set[uuid.UUID] = self._subscribers_by_symbol[asset_id]
                for client_id in subscribers:  # type: uuid.UUID
                    await self.send_message(client_id, point)

    def subscribe(self, client_id: uuid.UUID, symbol_id: int) -> None:
        self._subscribers_by_id[client_id] = symbol_id
        self._subscribers_by_symbol[symbol_id].add(client_id)
        logger.info(f"User subscribed on {symbol_id}")

    def unsubscribe(self, client_id: uuid.UUID) -> None:
        if symbol_id := self._subscribers_by_id.get(client_id):  # type: int
            subscribers: set[uuid.UUID] = self._subscribers_by_symbol[symbol_id]
            subscribers.discard(client_id)
            logger.info(f"User unsubscribed on {symbol_id}")

    async def send_message(self, client_id: uuid.UUID, message: dict) -> None:
        await self._connected_clients[client_id].send_str(orjson.dumps(message).decode())
