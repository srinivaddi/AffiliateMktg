import pytest
from starlette.responses import PlainTextResponse

from affiliate_mktg.src.api import middleware

import os
os.environ["SESSION_SECRET_KEY"] = "dummy_secret"

class DummyURL:
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self.path


class DummyRequest:
    def __init__(self, method="GET", path="/"):
        self.method = method
        self.url = DummyURL(path)


@pytest.mark.asyncio
async def test_logging_middleware_dispatch_returns_response_and_logs(monkeypatch):
    called = {"info": False}

    class DummyLogger:
        def info(self, msg, *args, **kwargs):
            called["info"] = True

    monkeypatch.setattr(middleware, "logger", DummyLogger())

    async def fake_call_next(request):
        return PlainTextResponse("ok", status_code=201)

    lm = middleware.LoggingMiddleware(app=None)
    resp = await lm.dispatch(DummyRequest(method="POST", path="/x"), fake_call_next)
    assert resp.status_code == 201
    assert called["info"]
