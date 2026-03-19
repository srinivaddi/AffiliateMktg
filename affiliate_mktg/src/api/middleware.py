import time
from starlette.middleware.base import BaseHTTPMiddleware

from affiliate_mktg.src.utils.logging_setup import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"Request: {request.method} {request.url} - Response : {response.status_code} - Time: {process_time:.4f}s"
        )
        return response
