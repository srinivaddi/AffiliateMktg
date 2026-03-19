import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import affiliate_mktg.src.config.amazon_loader as al

@pytest.mark.asyncio
async def test_get_amazon_config(monkeypatch):
    monkeypatch.setenv("ACCESS_KEY_PAAPI", "access")
    monkeypatch.setenv("SECRET_KEY_PAAPI", "secret")
    monkeypatch.setenv("PARTNER_TAG", "partner")
    monkeypatch.setenv("ENCRYPTION_KEY", "encrypt")
    monkeypatch.setenv("MARKETPLACE", "US")
    monkeypatch.setenv("THROTTLE_DELAY", "1")
    monkeypatch.setenv("HOST", "amazon.com")
    monkeypatch.setenv("REGION", "us-east-1")
    monkeypatch.setenv("CREDENTIAL_ID_CREATORSAPI", "creator_id")
    monkeypatch.setenv("CREDENTIAL_SECRET_CREATORSAPI", "creator_secret")
    monkeypatch.setenv("VERSION_CREATORSAPI", "v1")

    result = al.get_amazon_config()

    assert result == {
        "ACCESS_KEY_PAAPI": "access",
        "SECRET_KEY_PAAPI": "secret",
        "PARTNER_TAG": "partner",
        "ENCRYPTION_KEY": "encrypt",
        "MARKETPLACE": "US",
        "THROTTLE_DELAY": "1",
        "HOST": "amazon.com",
        "REGION": "us-east-1",
        "CREDENTIAL_ID_CREATORSAPI": "creator_id",
        "CREDENTIAL_SECRET_CREATORSAPI": "creator_secret",
        "VERSION_CREATORSAPI": "v1",
    }

@pytest.mark.asyncio
async def test_get_amazon_config_with_missing_env_vars(monkeypatch):
    monkeypatch.delenv("ACCESS_KEY_PAAPI", raising=False)
    monkeypatch.delenv("SECRET_KEY_PAAPI", raising=False)

    result = al.get_amazon_config()

    assert result["ACCESS_KEY_PAAPI"] is None
    assert result["SECRET_KEY_PAAPI"] is None