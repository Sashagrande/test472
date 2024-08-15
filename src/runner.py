import asyncio
import contextlib
import signal

import click
from aiohttp import web
from loguru import logger

from src import resources
from src.points import service
from src.points.server import websocket_server


@click.group()
def cli():
    pass


@click.option("--symbols", help="Comma-separated list of stores.")
@cli.command()
def run(symbols: str):
    asyncio.run(run_async(symbols.split(",")))


@contextlib.asynccontextmanager
async def graceful_shutdown(stop_event: asyncio.Event):
    def shutdown():
        logger.info("graceful shutdown")
        stop_event.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)
    yield


async def run_async(symbols):
    stop_event = asyncio.Event()

    server = websocket_server()
    runner = web.AppRunner(server)

    async with graceful_shutdown(stop_event), resources.context():
        try:
            task = asyncio.create_task(service.autorefresh(stop_event, symbols))
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", 8080)  # env
            await site.start()
            logger.info("websocket listen 0.0.0.0:8080")
            await stop_event.wait()
        except KeyboardInterrupt:
            logger.info("Server stopped manually")
        finally:
            await task
            await runner.cleanup()


if __name__ == "__main__":
    cli()
