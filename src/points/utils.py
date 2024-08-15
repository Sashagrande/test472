import asyncio
import datetime

from src.points import repository

background_tasks = set()


def build_point_message(asset_id: int, asset_name: str, created: datetime.datetime, rate: float):
    return {
        "assetName": asset_name,
        "assetId": asset_id,
        "time": int(created.timestamp()),
        "value": rate,
    }


def create_shielded_task(coro):
    task = asyncio.create_task(coro)
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    return task


async def parse_points(data):
    points = []
    *_, by_id = await repository.get_symbols()
    for point in data:
        point_data = {
            "assetName": by_id[point["symbol_id"]],
            "time": int(point["created"].timestamp()),
            "value": point["rate"],
            "assetId": point["symbol_id"],
        }
        points.append(point_data)
    return points
