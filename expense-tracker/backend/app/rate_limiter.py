from fastapi_limiter.depends import RateLimiter as _RateLimiter
from starlette.requests import Request
from starlette.responses import Response

class PatchedRateLimiter(_RateLimiter):
    """
    A patched RateLimiter for fastapi-limiter to work around the
    '_IncludedRouter object has no attribute path' issue in newer FastAPI versions.
    """
    async def __call__(self, request: Request, response: Response):
        route_index = 0
        dep_index = 0
        for i, route in enumerate(request.app.routes):
            if (
                getattr(route, "path", None) == request.scope["path"]
                and hasattr(route, "methods")
                and request.method in route.methods
            ):
                route_index = i
                if hasattr(route, "endpoint") and getattr(
                    route.endpoint, "_skip_limiter", False
                ):
                    return
                for j, dependency in enumerate(getattr(route, "dependencies", [])):
                    if self is dependency.dependency:
                        dep_index = j
                        break

        rate_key = await self.identifier(request)
        key = f"{rate_key}:{route_index}:{dep_index}"
        success = await self.limiter.try_acquire_async(key, blocking=self.blocking)
        if not success:
            return await self.callback(request, response)
