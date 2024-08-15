import contextlib
from types import SimpleNamespace

import aiohttp

from src.resources import demands

app = SimpleNamespace(session=None, headers={})


@contextlib.asynccontextmanager
async def context(*, client_session=app.session):
    app.session = client_session or aiohttp.ClientSession(
        base_url="https://rates.emcont.com/",  # env
        headers={"Content-Type": "application/json"},
    )
    async with app.session:
        yield


demands.add(context)
