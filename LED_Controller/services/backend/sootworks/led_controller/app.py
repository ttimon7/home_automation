import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sootworks.led_controller import APP_DIR
from sootworks.led_controller.containers import Container
from sootworks.led_controller.controller import get_color_endpoints, get_power_endpoint
from sootworks.led_controller.infrastructure.logging import set_up_logging
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


set_up_logging()


def configure_application_and_routes(app: FastAPI) -> None:
    for router_getter in (get_color_endpoints, get_power_endpoint):
        app.include_router(router_getter())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    container = Container()
    app.container = container
    configure_application_and_routes(app=app)

    app.mount("/", StaticFiles(directory=APP_DIR / "static"), name="static")
    app.mount("/assets", StaticFiles(directory=APP_DIR / "static/assets"), name="assets")

    yield

    logger.info("Shutting down LED Controller Service.")


# Run fastapi webserver.
app = FastAPI(lifespan=lifespan)


def log_http_request_errors(request: Request, status_code: str, reason: str) -> None:
    # TODO make sure traceback is logged too.
    error_message = (
        "HTTPException occurred. "
        f"Status code: {status_code} "
        f"Request method: {request.method} "
        f"Endpoint: {request.url}"
        f"Reason: {reason} "
    )
    logger.error(error_message)


@app.exception_handler(HTTPException)
async def custom_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    log_http_request_errors(
        request=request,
        status_code=exc.status_code,
        reason=exc.detail,
    )

    return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)


origins_regex = r"http://(localhost|192\.168\.0\.[0-9]{1,3}):{0,1}[0-9]{0,6}"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origins_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Callable:
    logger.info(f"Incoming request: {request.method} {request.url}")
    return await call_next(request)
