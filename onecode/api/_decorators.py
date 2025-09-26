import functools
import inspect
from typing import Callable, Optional

import httpx

from .utils import api_timeout


def with_httpx_client(
    param_name: str = "client",
    **client_kwargs
):
    """
    Decorator that injects an httpx.AsyncClient into an async function.

    If the function already receives a client via `param_name`, it is reused.
    Otherwise, one is created with `client_kwargs` and closed after the function runs.

    """

    def decorator(func: Callable):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("@with_httpx_client can only be applied to async functions")

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            client: Optional[httpx.AsyncClient] = kwargs.get(param_name)
            own_client = False

            if client is None:
                client = httpx.AsyncClient(timeout=api_timeout(), **client_kwargs)
                kwargs[param_name] = client
                own_client = True

            try:
                return await func(*args, **kwargs)
            finally:
                if own_client:
                    await client.aclose()

        return wrapper

    return decorator
