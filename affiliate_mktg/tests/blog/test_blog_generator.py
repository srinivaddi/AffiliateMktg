import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from affiliate_mktg.src.blog.blog_generator import BlogGenerator
import ollama
import affiliate_mktg.src.blog.blog_generator as bg

@pytest.mark.asyncio
async def test_generate_blog_by_model_llama(monkeypatch):
    gen = bg.BlogGenerator()
    monkeypatch.setattr(
        bg.BlogGenerator,
        "_generate_blog_llama",
        AsyncMock(return_value="blog"),
    )
    result = await gen.generate_blog_by_model(
        "sys", "user", "llama3.1", {}
    )
    assert result == "blog"

@pytest.mark.asyncio
async def test_generate_blog_by_model_invalid(monkeypatch):
    gen = bg.BlogGenerator()
    with pytest.raises(ValueError):
        await gen.generate_blog_by_model("sys", "user", "other", {})


@pytest.mark.asyncio
async def test_generate_blog_by_model_stream_llama(monkeypatch):
    gen = bg.BlogGenerator()
    monkeypatch.setattr(
        bg.BlogGenerator,
        "_generate_blog_llama_stream",
        AsyncMock(return_value="blog"),
    )
    result = await gen.generate_blog_by_model_stream(
        "sys", "user", "llama3.1", {}
    )
    assert result == "blog"

@pytest.mark.asyncio
async def test_generate_blog_by_model_stream_invalid(monkeypatch):
    gen = bg.BlogGenerator()
    with pytest.raises(ValueError):
        await gen.generate_blog_by_model_stream(
            "sys", "user", "other", {}
        )
        
@pytest.mark.asyncio
async def test_generate_blog_llama_success(monkeypatch):
    gen = bg.BlogGenerator()
    mock_response = {
        "message": {
            "content": "Generated blog content"
        }
    }
    monkeypatch.setattr(
        bg.ollama,
        "chat",
        MagicMock(return_value=mock_response),
    )
    result = await gen._generate_blog_llama("sys", "user", {})
    assert result == "Generated blog content"

@pytest.mark.asyncio
async def test_generate_blog_llama_response_error(monkeypatch):
    gen = bg.BlogGenerator()
    monkeypatch.setattr(
        bg.ollama,
        "chat",
        MagicMock(side_effect=ollama.ResponseError(status_code=404, error="not found")),
    )
    result = await gen._generate_blog_llama("sys", "user", {})
    assert result == ""

@pytest.mark.asyncio
async def test_generate_blog_llama_exception(monkeypatch):
    gen = bg.BlogGenerator()
    monkeypatch.setattr(
        bg.ollama,
        "chat",
        MagicMock(side_effect=Exception("fail")),
    )
    monkeypatch.setattr(
        bg,
        "logger",
        MagicMock(),
    )
    result = await gen._generate_blog_llama("sys", "user", {})
    assert result == ""

@pytest.mark.asyncio
async def test_generate_blog_llama_stream_success(monkeypatch):
    gen = BlogGenerator()
    mock_async_client = MagicMock()
    class DummyAsync:
        async def __aiter__(self):
            yield {"message": {"content": "blog"}}
    async def mock_chat(**kwargs):
        return DummyAsync()
    mock_async_client.return_value.chat = mock_chat
    monkeypatch.setattr('affiliate_mktg.src.blog.blog_generator.AsyncClient', mock_async_client)
    result = await gen._generate_blog_llama_stream('sys', 'user', {})
    assert result == 'blog'

@pytest.mark.asyncio
async def test_generate_blog_llama_stream_response_error(monkeypatch):
    gen = BlogGenerator()
    class DummyResponseError(Exception):
        status_code = 404
        error = 'not found'
    mock_async_client = MagicMock()
    async def mock_chat(**kwargs):
        raise DummyResponseError()
    mock_async_client.return_value.chat = mock_chat
    monkeypatch.setattr('affiliate_mktg.src.blog.blog_generator.AsyncClient', mock_async_client)
    monkeypatch.setattr('affiliate_mktg.src.blog.blog_generator.logger', MagicMock())
    result = await gen._generate_blog_llama_stream('sys', 'user', {})
    assert result == ''

@pytest.mark.asyncio
async def test_generate_blog_llama_stream_exception(monkeypatch):
    gen = BlogGenerator()
    mock_async_client = MagicMock()
    async def mock_chat(**kwargs):
        raise Exception('fail')
    mock_async_client.return_value.chat = mock_chat
    monkeypatch.setattr('affiliate_mktg.src.blog.blog_generator.AsyncClient', mock_async_client)
    monkeypatch.setattr('affiliate_mktg.src.blog.blog_generator.logger', MagicMock())
    result = await gen._generate_blog_llama_stream('sys', 'user', {})
    assert result == ''
