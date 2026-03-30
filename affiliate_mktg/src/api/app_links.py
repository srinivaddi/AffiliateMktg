import json
import uuid
from datetime import date

from affiliate_mktg.src.utils.logging_setup import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware
from starlette.middleware import Middleware

from affiliate_mktg.src.api.middleware import LoggingMiddleware
from affiliate_mktg.src.mcp.server import mcp_server
from affiliate_mktg.src.mcp.mcp_wrapper import MCPToolInvoker
from affiliate_mktg.src.utils.json_response import PrettyJSONResponse, GetJSONResponseData
from affiliate_mktg.src.core.models import SearchInput
from affiliate_mktg.src.core.enums import AvailabilityType
from affiliate_mktg.src.config.loader import get_starlette_config

configValues = get_starlette_config()

async def ensure_session_cookie(request: Request, call_next):
    session = request.session
    if "session_id" not in session:
        cookie_session_id = request.cookies.get("session")
        if cookie_session_id:
            session["session_id"] = cookie_session_id
        else:
            session["session_id"] = str(uuid.uuid4())

    if "request_counts" not in session:
        cookie_request_counts = request.cookies.get("request_counts")
        if cookie_request_counts not in (None, "{}"):
            session["request_counts"] = json.loads(cookie_request_counts)

    response = await call_next(request)

    if "session" not in request.cookies:
        response.set_cookie(
            key="session",
            value=session["session_id"],
            httponly=True,
            path="/",
            max_age=86400,
            samesite="Lax",
        )

    return response


async def post_request_counter_middleware(request: Request, call_next):
    today = str(date.today())
    session = request.session
    session_id = session.get("session_id")

    if session_id:
        if (
            request.method == configValues["POST"]
            and request.url.path
            == configValues["RUN_GENERATE_LINK_POST_BLOG_MANUAL_PATH"]
        ):
            if "request_counts" not in session:
                session["request_counts"] = {}
            session["request_counts"][today] = (
                session["request_counts"].get(today, 0) + 1
            )

        if (
            request.method == configValues["GET"]
            and request.url.path == configValues["STATS_PATH"]
        ):
            if "request_counts" not in session:
                session["request_counts"] = {}
            session["request_counts"][today] = session["request_counts"].get(
                today, 0
            )

    response = await call_next(request)
    return response


def _coerce_availability_type(value) -> AvailabilityType:
    """Coerce string from API to AvailabilityType enum."""
    if value is None:
        return AvailabilityType.INSTOCK
    if isinstance(value, AvailabilityType):
        return value
    if isinstance(value, str):
        for e in AvailabilityType:
            if e.value == value:
                return e
        return AvailabilityType.INSTOCK
    return AvailabilityType.INSTOCK


class App_Links:
    def get_routes(self):
        return [
            Route(self.HOMEPAGE_PATH, self.homepage, methods=["GET"]),
            Route(self.STATS_PATH, self.get_session_state, methods=["GET"]),
            Route(self.RESET_STATS_PATH, self.reset_session, methods=["POST"]),
            Route(self.HEALTH_PATH, self.health_check, methods=["GET"]),
            Route(
                self.RUN_GENERATE_LINK_POST_BLOG_MANUAL_PATH,
                self.run_generate_link_post_blog_manual,
                methods=["POST"],
            ),
        ]

    async def custom_http_exception_handler(self, request, exc):
        return JSONResponse(
            {"detail": exc.detail}, status_code=exc.status_code
        )

    async def custom_value_error_handler(self, request, exc):
        return PlainTextResponse(
            f"Custom error handling for: {exc}", status_code=500
        )

    def __init__(self):
        logger.info("Hello from App starlette!")
        self.read_config_values()
        self.setup_starlette_app()

    def read_config_values(self):
        self.SESSION_SECRET_KEY = configValues["SESSION_SECRET_KEY"]
        self.HOMEPAGE_PATH = configValues["HOMEPAGE_PATH"]
        self.SESSION_PATH = configValues["SESSION_PATH"]
        self.STATS_PATH = configValues["STATS_PATH"]
        self.RESET_STATS_PATH = configValues["RESET_STATS_PATH"]
        self.HEALTH_PATH = configValues["HEALTH_PATH"]
        self.RUN_GENERATE_LINK_POST_BLOG_MANUAL_PATH = configValues[
            "RUN_GENERATE_LINK_POST_BLOG_MANUAL_PATH"
        ]

    def setup_starlette_app(self):
        middleware = self.get_starlette_middleware()
        self.app = Starlette(
            debug=True, routes=self.get_routes(), middleware=middleware
        )

    def get_starlette_middleware(self):
        return [
            Middleware(
                SessionMiddleware,
                secret_key=self.SESSION_SECRET_KEY,
                max_age=86400,
            ),
            Middleware(
                BaseHTTPMiddleware, dispatch=ensure_session_cookie
            ),
            Middleware(
                BaseHTTPMiddleware,
                dispatch=post_request_counter_middleware,
            ),
            Middleware(
                CORSMiddleware,
                allow_origins=[
                    "http://localhost:8501/",
                    "http://localhost:8000",
                    "https://mydomain.com",
                ],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
                expose_headers=["Set-Cookie"],
                max_age=86400,
            ),
            Middleware(
                TrustedHostMiddleware,
                allowed_hosts=["mydomain.com", "*.mydomain.com", "localhost"],
            ),
            Middleware(
                ExceptionMiddleware,
                handlers={
                    404: self.custom_http_exception_handler,
                    ValueError: self.custom_value_error_handler,
                    500: PlainTextResponse("Internal Server Error"),
                },
            ),
            Middleware(LoggingMiddleware),
        ]

    async def receive_json(self, request):
        if (
            request.method == "POST"
            and "application/json"
            in request.headers.get("Content-Type", "")
        ):
            data = await request.json()
            return JSONResponse({"received_data": data})
        return JSONResponse(
            {"error": "Please send a POST request with JSON body"},
            status_code=400,
        )

    async def reset_session(self, request):
        request.session.clear()
        return PlainTextResponse("Session reset.")

    async def get_session_state(self, request: Request):
        session = request.session
        session_id = session.get("session_id")
        request_counts = session.get("request_counts", {})
        return JSONResponse(
            {"session_id": session_id, "request_counts": request_counts}
        )

    async def homepage(self, request):
        return JSONResponse(
            {"message": "Welcome to the Starlette MPC server!"}
        )

    async def health_check(self, request: Request) -> JSONResponse:
        mcp_servers = [mcp_server]
        mcp_server_names = ["AffiliateMarketingBlogPostMCPServer"]
        mcp_tool_names = ["generate_link_post_blog_manual_tool"]
        result_health = []
        try:
            for server in mcp_servers:
                is_server_available = server in mcp_servers
                is_server_name_available = server.name in mcp_server_names
                tool_registry = self._get_tool_names(server)
                for tool in tool_registry:
                    is_tool_available = tool in mcp_tool_names
                    status = "OK" if is_tool_available else "ERROR"
                    status_code = 200 if is_tool_available else 500
                    result_health.append({
                        "status": status,
                        "server": server.name,
                        "server_available": is_server_available,
                        "tool": tool,
                        "tool_available": is_tool_available
                        and is_server_name_available,
                        "status_code": status_code,
                    })
            return PrettyJSONResponse({"health": result_health})
        except Exception as e:
            logger.error(
                f"An error occurred in health check: {str(e)}",
                exc_info=True,
            )
            return JSONResponse(
                {"status": "ERROR", "message": str(e)},
                status_code=500,
            )

    def _get_tool_names(self, mcp_server):
        try:
            tool_dict = getattr(mcp_server, "_tool_manager", None)
            if tool_dict is None or not hasattr(tool_dict, "_tools"):
                return []
            tools = tool_dict._tools
            if isinstance(tools, dict):
                return list(tools.keys())
            return []
        except Exception as e:
            logger.error(
                f"An error occurred in get tool names method: {str(e)}",
                exc_info=True,
            )
            return []

    async def run_generate_link_post_blog_manual(self, request: Request):
        response = await self.receive_json(request)
        data = GetJSONResponseData(response)

        search_input = self._get_param_values(data)
        if search_input:
            try:
                invoker = MCPToolInvoker(mcp_server)
                result = await invoker.invoke_tool(
                    "generate_link_post_blog_manual_tool",
                    searchInput=search_input,
                )
                return JSONResponse({
                    "result": result,
                    "session_id": request.session.get("session_id"),
                    "request_counts": request.session.get(
                        "request_counts"
                    ),
                })
            except Exception as e:
                logger.error(
                    f"An error occurred in run generate link post blog manual method: {str(e)}",
                    exc_info=True,
                )
                return JSONResponse(
                    {"error": str(e)}, status_code=500
                )
        return JSONResponse(
            {"error": "Invalid input parameters"}, status_code=400
        )

    def _get_param_values(self, data) -> SearchInput | None:
        search_input = None
        try:
            if "received_data" not in data.body:
                return None
            outer_value = data.body.get("received_data")
            inner = outer_value.get("src") if "src" in outer_value else outer_value
            if not inner:
                return None
            search_input = SearchInput(
                keywords=inner["keywords"],
                search_index=inner["search_index"],
                item_count=int(inner["item_count"]),
                # show_availability_type=_coerce_availability_type(
                #     inner.get("show_availability_type")
                # ),
                show_availability_type=list(inner.get("show_availability_type")),
                show_prime_delivery_items=bool(
                    inner.get("show_prime_delivery_items")
                ),
                show_isprimeexclusive_items=bool(
                    inner.get("show_isprimeexclusive_items")
                ),
                show_isbuyboxwinner_items=bool(
                    inner.get("show_isbuyboxwinner_items")
                ),
                show_freeshipping_items=bool(
                    inner.get("show_freeshipping_items")
                ),
                show_discount_items=bool(inner.get("show_discount_items")),
                discount_percentage=int(
                    inner.get("discount_percentage", 0)
                ),
            )
            return search_input
        except Exception as e:
            logger.error(
                f"An error occurred in get param values method: {str(e)}",
                exc_info=True,
            )
            return search_input


app = App_Links().app
