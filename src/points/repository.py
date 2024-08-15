from async_lru import alru_cache
from envparse import env

from src.resources.postgres import request_pool

db = request_pool(
    env.str("POSTGRES_DSN", default="postgres://postgres:postgres@localhost:5432/postgres")
)


@alru_cache(ttl=20)
async def get_symbols(*, pg=db):
    data = await pg.fetch(
        "SELECT id, symbol FROM symbols",
    )
    result_by_symbol = {}
    result_by_id = {}
    for symbol in data:
        result_by_symbol[symbol["symbol"]] = symbol["id"]
        result_by_id[symbol["id"]] = symbol["symbol"]
    return result_by_symbol, result_by_id


async def save(data, *, pg=db):
    await pg.execute(
        """
        INSERT INTO points
        SELECT id, rate, created
        FROM unnest($1::int[], $2::numeric[], $3::timestamp[]) AS t(id, rate, created)
        """,
        *zip(*data)
    )
    get_history.cache_clear()


@alru_cache(ttl=0.1)
async def get_history(symbol_id, *, pg=db):
    return await pg.fetch(
        "SELECT symbol_id, rate, created "
        "FROM points "
        "WHERE symbol_id=$1 AND created >= CURRENT_TIMESTAMP - INTERVAL '30 MINUTES'"
        "ORDER BY created DESC",
        symbol_id,
    )
