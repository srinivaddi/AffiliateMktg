import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import affiliate_mktg.src.config.loader as lod
from itsdangerous import URLSafeSerializer

@pytest.mark.asyncio
async def test_get_blog_config(monkeypatch):
    monkeypatch.setenv("BLOG_ID", "blog123")
    monkeypatch.setenv("SCOPES_STR", "scope")
    monkeypatch.setenv("SERVICE_NAME", "blogger")
    monkeypatch.setenv("SERVICE_VERSION", "v3")
    monkeypatch.setenv("BASE_URL", "https://example.com")
    monkeypatch.setenv("LABELS", "tech,ai")
    monkeypatch.setenv("LIVE_POST", "true")
    monkeypatch.setenv("FILE_EXTENSION", ".md")
    monkeypatch.setenv("LOCATION_JSON", "/tmp/location.json")
    monkeypatch.setenv("CLIENT_SECRETS_JSON", "{}")
    monkeypatch.setenv("FILTER_POST_COUNT", "10")
    monkeypatch.setenv("FILTER_POST", "true")
    monkeypatch.setenv("FILTER_DAYS", "7")
    monkeypatch.setenv("MODEL_NAME", "gpt")
    monkeypatch.setenv("MODEL_OPTIONS_JSON", "{}")
    monkeypatch.setenv("TOPIC", "ai")
    monkeypatch.setenv("STREAM", "false")
    monkeypatch.setenv("SYSTEM_PROMPT_ROLE", "system")
    monkeypatch.setenv("SYSTEM_PROMPT_STYLE", "formal")
    monkeypatch.setenv("SYSTEM_PROMPT_TEMPLATE", "template")
    monkeypatch.setenv("USER_PROMPT_TEMPLATE", "user_template")

    result = lod.get_blog_config()

    assert result == {
        "BLOG_ID": "blog123",
        "SCOPES_STR": "scope",
        "SERVICE_NAME": "blogger",
        "SERVICE_VERSION": "v3",
        "BASE_URL": "https://example.com",
        "LABELS": "tech,ai",
        "LIVE_POST": "true",
        "FILE_EXTENSION": ".md",
        "LOCATION_JSON": "/tmp/location.json",
        "CLIENT_SECRETS_JSON": "{}",
        "FILTER_POST_COUNT": "10",
        "FILTER_POST": "true",
        "FILTER_DAYS": "7",
        "MODEL_NAME": "gpt",
        "MODEL_OPTIONS_JSON": "{}",
        "TOPIC": "ai",
        "STREAM": "false",
        "SYSTEM_PROMPT_ROLE": "system",
        "SYSTEM_PROMPT_STYLE": "formal",
        "SYSTEM_PROMPT_TEMPLATE": "template",
        "USER_PROMPT_TEMPLATE": "user_template",
    }
    
@pytest.mark.asyncio
async def test_get_blog_config_missing_env_vars(monkeypatch):
    monkeypatch.delenv("BLOG_ID", raising=False)
    result = lod.get_blog_config()
    assert result["BLOG_ID"] is None
    
@pytest.mark.asyncio
async def test_get_starlette_config(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET_KEY", "secret-key")
    monkeypatch.setenv("HOMEPAGE_PATH", "/")
    monkeypatch.setenv("SESSION_PATH", "/session")
    monkeypatch.setenv("STATS_PATH", "/stats")
    monkeypatch.setenv("RESET_STATS_PATH", "/reset")
    monkeypatch.setenv("HEALTH_PATH", "/health")
    monkeypatch.setenv("RUN_GENERATE_LINK_POST_BLOG_MANUAL_PATH", "/run")
    monkeypatch.setenv("GET", "GET")
    monkeypatch.setenv("POST", "POST")

    result = lod.get_starlette_config()

    assert result["SESSION_SECRET_KEY"] == "secret-key"
    assert result["HOMEPAGE_PATH"] == "/"
    assert result["SESSION_PATH"] == "/session"
    assert result["STATS_PATH"] == "/stats"
    assert result["RESET_STATS_PATH"] == "/reset"
    assert result["HEALTH_PATH"] == "/health"
    assert result["RUN_GENERATE_LINK_POST_BLOG_MANUAL_PATH"] == "/run"
    assert result["GET"] == "GET"
    assert result["POST"] == "POST"

    serializer = result["SERIALLIZER"]
    assert isinstance(serializer, URLSafeSerializer)

    token = serializer.dumps({"user": "test"})
    assert serializer.loads(token) == {"user": "test"}