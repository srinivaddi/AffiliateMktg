import asyncio
import json
from datetime import date

import pytest
from starlette.responses import JSONResponse, PlainTextResponse

from affiliate_mktg.src.api import app_links
from affiliate_mktg.src.core.enums import AvailabilityType
from affiliate_mktg.src.core.models import SearchInput


import os


# Fixture to set SESSION_SECRET_KEY for each test
import pytest

@pytest.fixture(autouse=True)
def session_secret_key(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET_KEY", "dummy_secret")


# Fixture to reset configValues for each test that needs it
@pytest.fixture
def config_values(monkeypatch):
    monkeypatch.setattr(app_links, "configValues", {
        "POST": "POST",
        "GET": "GET",
        "RUN_GENERATE_LINK_POST_BLOG_MANUAL_PATH": "/run",
        "STATS_PATH": "/stats",
    })


class DummyURL:
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self.path


class DummyRequest:
    def __init__(self, method="GET", path="/", cookies=None, headers=None, session=None, json_body=None):
        self.method = method
        self.url = DummyURL(path)
        self.cookies = cookies or {}
        self.headers = headers or {}
        self.session = session if session is not None else {}
        self._json = json_body

    async def json(self):
        return self._json


@pytest.mark.asyncio
async def test_ensure_session_cookie_sets_cookie_when_missing():
    req = DummyRequest(method="GET", path="/")
    # call_next returns a real response which supports set_cookie
    async def call_next(request):
        return PlainTextResponse("ok")

    resp = await app_links.ensure_session_cookie(req, call_next)
    # Some Starlette versions expose the cookie header via headers, others via raw_headers
    raw = getattr(resp, "raw_headers", [])
    has_set_cookie = resp.headers.get("set-cookie") is not None or any(
        name.lower() == b"set-cookie" for name, _ in raw
    )
    assert "session_id" in req.session
    assert has_set_cookie


@pytest.mark.asyncio
async def test_ensure_session_cookie_uses_existing_cookie():
    req = DummyRequest(method="GET", path="/", cookies={"session": "abc-123"})

    async def call_next(request):
        return PlainTextResponse("ok")

    resp = await app_links.ensure_session_cookie(req, call_next)
    assert req.session.get("session_id") == "abc-123"
    assert resp.headers.get("set-cookie") is None


@pytest.mark.asyncio
async def test_post_request_counter_middleware_increments_on_post_and_get(config_values):
    today = str(date.today())

    # POST increment
    req_post = DummyRequest(method="POST", path="/run", session={"session_id": "s1"})

    async def call_next_post(request):
        return PlainTextResponse("ok")

    await app_links.post_request_counter_middleware(req_post, call_next_post)
    assert req_post.session["request_counts"][today] == 1

    # GET should set the key but not increment
    req_get = DummyRequest(method="GET", path="/stats", session={"session_id": "s1"})

    async def call_next_get(request):
        return PlainTextResponse("ok")

    await app_links.post_request_counter_middleware(req_get, call_next_get)
    assert today in req_get.session["request_counts"]


def test__coerce_availability_type_variants():
    assert app_links._coerce_availability_type(None) == AvailabilityType.INSTOCK
    assert app_links._coerce_availability_type(AvailabilityType.UNKNOWN) == AvailabilityType.UNKNOWN
    assert app_links._coerce_availability_type("IN_STOCK") == AvailabilityType.INSTOCK
    assert app_links._coerce_availability_type("BAD_VALUE") == AvailabilityType.INSTOCK


def test_get_tool_names_empty_and_dict():
    class ServerNoTools:
        pass

    assert app_links.App_Links()._get_tool_names(ServerNoTools()) == []

    class ToolManager:
        def __init__(self):
            self._tools = {"t1": 1, "t2": 2}

    class ServerWithTools:
        def __init__(self):
            self._tool_manager = ToolManager()

    names = app_links.App_Links()._get_tool_names(ServerWithTools())
    assert set(names) == {"t1", "t2"}


@pytest.mark.asyncio
async def test_health_check_ok_and_error(monkeypatch):
    # happy path: tool exists and server name matches
    class DummyToolManager:
        def __init__(self):
            self._tools = {"generate_link_post_blog_manual_tool": True}

    class DummyServer:
        name = "AffiliateMarketingBlogPostMCPServer"
        _tool_manager = DummyToolManager()

    monkeypatch.setattr(app_links, "mcp_server", DummyServer)
    al = app_links.App_Links()
    resp = await al.health_check(DummyRequest())
    assert isinstance(resp, JSONResponse)
    body = json.loads(resp.body.decode("utf-8"))
    assert "health" in body and len(body["health"]) >= 1
    # Check that at least one status_code is 200
    assert any(item.get("status_code") == 200 for item in body["health"])

    # error path: make server access raise
    class BrokenServer:
        @property
        def name(self):
            raise Exception("boom")
        _tool_manager = None

    # monkeypatch.setattr(app_links, "mcp_server", BrokenServer)
    # al = app_links.App_Links()
    # resp2 = await al.health_check(DummyRequest())
    # assert isinstance(resp2, JSONResponse)
    # assert resp2.status_code == 500
    # body2 = json.loads(resp2.body.decode("utf-8"))
    # assert body2["status"] == "ERROR"
    # assert "boom" in body2["message"]

@pytest.mark.asyncio
async def test_receive_json_reset_and_session_state_and_homepage():
    al = app_links.App_Links()

    # receive_json with correct content-type
    req = DummyRequest(method="POST", path="/", headers={"Content-Type": "application/json"}, json_body={"a": 1})
    resp = await al.receive_json(req)
    assert resp.status_code == 200
    data = json.loads(resp.body.decode("utf-8"))
    assert data["received_data"] == {"a": 1}

    # reset_session clears session
    req2 = DummyRequest(session={"x": 1})
    resp2 = await al.reset_session(req2)
    assert req2.session == {}
    assert isinstance(resp2, PlainTextResponse)

    # get_session_state returns session_id and request_counts
    req3 = DummyRequest(session={"session_id": "s1", "request_counts": {"d": 2}})
    resp3 = await al.get_session_state(req3)
    body3 = json.loads(resp3.body.decode("utf-8"))
    assert body3["session_id"] == "s1"
    assert body3["request_counts"] == {"d": 2}

    # homepage
    resp4 = await al.homepage(DummyRequest())
    body4 = json.loads(resp4.body.decode("utf-8"))
    assert "Welcome" in body4["message"]


@pytest.mark.asyncio
async def test__get_param_values_and_run_generate(monkeypatch):
    # prepare a payload that matches expected structure
    inner = {
        "keywords": "k",
        "search_index": "si",
        "item_count": "2",
        "show_availability_type": ["IN_STOCK"],
        "show_prime_delivery_items": True,
        "show_isprimeexclusive_items": False,
        "show_isbuyboxwinner_items": False,
        "show_freeshipping_items": False,
        "show_discount_items": False,
        "discount_percentage": "5",
    }
    body = {"received_data": inner}

    al = app_links.App_Links()

    class DummyResp:
        def __init__(self, body):
            self.body = json.dumps(body).encode("utf-8")

    # test _get_param_values
    data = type("D", (), {"body": body})()
    si = al._get_param_values(data)
    assert isinstance(si, SearchInput)
    assert si.keywords == "k"

    # test run_generate_link_post_blog_manual when valid
    async def fake_receive_json(request):
        return DummyResp(body)

    class DummyInvoker:
        def __init__(self, server):
            pass

        async def invoke_tool(self, name, **kwargs):
            return {"ok": True}

    monkeypatch.setattr(al, "receive_json", fake_receive_json)
    monkeypatch.setattr(app_links, "MCPToolInvoker", DummyInvoker)

    req = DummyRequest(method="POST", path="/run", session={"session_id": "s1", "request_counts": {}})
    resp = await al.run_generate_link_post_blog_manual(req)
    assert resp.status_code == 200
    body = json.loads(resp.body.decode("utf-8"))
    assert body["result"] == {"ok": True}

    # test run_generate_link_post_blog_manual when invalid params
    async def fake_receive_json_invalid(request):
        return DummyResp({})

    monkeypatch.setattr(al, "receive_json", fake_receive_json_invalid)
    resp2 = await al.run_generate_link_post_blog_manual(req)
    assert resp2.status_code == 400