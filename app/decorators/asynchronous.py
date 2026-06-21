import functools
import anyio


def run_as_async(func):
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        bound_func = functools.partial(func, *args, **kwargs)
        return await anyio.to_thread.run_sync(bound_func)

    return async_wrapper
