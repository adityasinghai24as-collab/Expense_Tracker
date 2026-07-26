import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI

logger = logging.getLogger(__name__)


class DomainException(Exception):
    """
    Base class for custom domain exceptions.
    Use this to raise business logic errors that should result in a specific HTTP response.
    """
    def __init__(self, name: str, detail: str, status_code: int = 400):
        self.name = name
        self.detail = detail
        self.status_code = status_code


def register_exception_handlers(app: FastAPI):
    """
    Register global and custom exception handlers for the FastAPI application.
    """
    
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        """Handler for specific domain errors"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.name,
                "detail": exc.detail
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        Global handler for unexpected 500 errors.
        Prevents raw stack traces from leaking to the client in production.
        """
        logger.error(f"Unhandled server error at {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred. Please try again later."
            },
        )
