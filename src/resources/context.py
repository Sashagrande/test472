from contextlib import AsyncExitStack
from typing import AsyncContextManager, AsyncGenerator, Callable

from src.resources.utils import single_async_context_manager

demands = set()


@single_async_context_manager
async def context() -> AsyncGenerator:
    async with AsyncExitStack() as stack:
        for ctx in demands:
            await stack.enter_async_context(ctx())
        yield stack
