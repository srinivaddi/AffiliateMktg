import json

import pytest
from starlette.responses import JSONResponse

from affiliate_mktg.src.utils.json_response import (
    PrettyJSONResponse,
    GetJSONResponseData,
)


def test_pretty_json_response_renders_pretty_json():
    content = {
        "name": "Affiliate Marketing",
        "count": 2,
        "active": True,
    }

    response = PrettyJSONResponse(content)
    body = response.body.decode("utf-8")

    # Must be valid JSON
    parsed = json.loads(body)
    assert parsed == content

    # Pretty formatting checks
    assert "\n" in body
    assert body.startswith("{\n")
    assert '    "name"' in body  # 4-space indent


def test_pretty_json_response_preserves_unicode():
    content = {
        "message": "café 🚀",
    }

    response = PrettyJSONResponse(content)
    body = response.body.decode("utf-8")

    assert "café" in body
    assert "🚀" in body

    parsed = json.loads(body)
    assert parsed["message"] == "café 🚀"


def test_pretty_json_response_returns_bytes():
    response = PrettyJSONResponse({"a": 1})
    assert isinstance(response.body, bytes)

def test_get_json_response_data_parses_body():
    content = {"status": "ok", "count": 3}
