import orjson

from src.points.client import app


async def load(request: dict | None = None):
    async with app.session.get(
        "/",  # env
        json=request,
        headers=app.headers,
    ) as response:
        if response.status != 200:
            # do something
            return None

        data = await response.text()
        return orjson.loads(data[5:-3])
