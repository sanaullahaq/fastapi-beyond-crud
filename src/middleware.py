import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

# Above code disables the default FastAPI Logging mechanism and starts our own custom logging via below code


def register_custom_logging_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)
        processing_time = time.time() - start_time

        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}s"

        print(message)
        return response


def register_cors_middleware(app: FastAPI):
    # https://fastapi.tiangolo.com/tutorial/cors/#use-corsmiddleware
    # origins = [
    #     "https://google.com",
    #     "https://youtube.com",
    # ]
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    """
    Basically we are allowing everybody(origins) to send API request to our server with `origins=["*"]`
    `allow_credentials=True` -> Credentials (Authorization headers, Cookies, etc).
    `allow_methods=["*"]` -> Specific HTTP methods (POST, PUT) or all of them with the wildcard "*".
    `allow_headers=["*"]` -> Specific HTTP headers or all of them with the wildcard "*".

    CORS - Cross-Origin Resource Sharing: comes handy when you server is made for private use, only
    request from specific origins will be allowed, only specific methods will be allowed. etc etc.
    """

    # Enforce security boundaries
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["example.com", "*.example.com", "localhost", "127.0.0.1", "bookly-nx51.onrender.com"],
    )

    """
    TrustedHostMiddleware locks down who your server will even talk to at the transport/request level;

    CORSMiddleware locks down which browser-based frontends are allowed to consume the response.
    
    Both are usually needed together — one doesn't substitute for the other.
    """