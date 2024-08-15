import asyncio
import datetime

from loguru import logger

from src.points import repository
from src.points.connections import BroadcastManager
from src.points.integration import load
from src.points.utils import build_point_message, create_shielded_task

manager = BroadcastManager()


async def autorefresh(stop_event, symbols):
    logger.info(f"Auto refreshing for {symbols} has started")
    symbols_ids, *_ = await repository.get_symbols()
    symbols_ids = dict(
        map(lambda x: (x, symbols_ids[x]), filter(lambda s: s in symbols, symbols_ids))
    )
    points_queue = {symbol_id: asyncio.Queue() for symbol_id in symbols_ids.values()}
    create_shielded_task(manager.broadcast(stop_event, points_queue))
    while not stop_event.is_set():
        data_for_db = []
        data = await load()
        created = datetime.datetime.utcnow()
        for symbol_data in filter(lambda t: t["Symbol"] in symbols, data["Rates"]):
            symbol_id = symbols_ids[symbol_data["Symbol"]]
            rate = (symbol_data["Bid"] + symbol_data["Ask"]) / 2
            data_for_db.append((symbol_id, rate, created))
            point_queue = points_queue[symbol_id]

            point = build_point_message(symbol_id, symbol_data["Symbol"], created, rate)
            await point_queue.put(point)

        create_shielded_task(repository.save(data_for_db))
        await asyncio.sleep(1)  # env


async def assets_handler(client_id, msg):
    assets_by_symbol, *_ = await repository.get_symbols()
    assets_data = []
    for name, _id in assets_by_symbol.items():
        assets_data.append({"id": _id, "name": name})
    message = {"action": msg["action"], "message": {"assets": assets_data}}
    await manager.send_message(client_id, message)


async def subscribe_handler(client_id, msg):
    manager.unsubscribe(client_id)
    asset_id = msg["message"]["assetId"]
    await manager.send_history(client_id, asset_id)
    manager.subscribe(client_id, asset_id)


HANDLERS = {
    "assets": assets_handler,
    "subscribe": subscribe_handler,
}


async def handle(msg: dict, client_id):
    action = msg["action"]
    handler = HANDLERS[action]
    create_shielded_task(handler(client_id, msg))
