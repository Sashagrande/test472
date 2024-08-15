import functools
from contextlib import asynccontextmanager

import asyncpg

from src.resources import demands


class Pool:
    _pool: asyncpg.Pool | None = None

    def __init__(self, dsn, **kw):
        self.dsn = dsn
        self.kw = kw

    def __call__(self, *args, **kwargs):
        return self

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.disconnect()

    @property
    def pool(self):
        return self._pool

    def __getattr__(self, attr):
        if self._pool is None:
            raise RuntimeError("Wrong initialization sequence.")
        return getattr(self._pool, attr)

    async def connect(self):
        if not self._pool:
            self._pool = await asyncpg.create_pool(dsn=self.dsn, **self.kw)

    async def disconnect(self):
        await self._pool.close()
        self._pool = None


def request_pool(
    dsn: str,
    *,
    min_size: int = 1,  # env
    max_size: int = 5,  # env
) -> asyncpg.Pool:
    pool = Pool(dsn, min_size=min_size, max_size=max_size)
    demands.add(pool)
    return pool
