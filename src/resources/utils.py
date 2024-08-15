import inspect
from contextlib import asynccontextmanager
from functools import wraps
from typing import AsyncGenerator


def single_async_context_manager(generator: AsyncGenerator):
    @asynccontextmanager
    @wraps(generator)
    async def wrapper(*args, **kwargs):
        if wrapper.is_running:
            module = inspect.getmodule(generator).__name__
            raise RuntimeError(f"Сontext from {module} is already in use.")
        wrapper.is_running = True
        async for item in generator(*args, **kwargs):
            yield item
        wrapper.is_running = False

    wrapper.is_running = False
    return wrapper
