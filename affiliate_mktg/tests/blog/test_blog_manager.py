import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from affiliate_mktg.src.blog.blog_manager import BlogManager
import affiliate_mktg.src.blog.blog_manager as bm

# @pytest.fixture(autouse=True)
# def patch_config(monkeypatch):
#     monkeypatch.setattr('affiliate_mktg.src.blog.blog_manager.configValues', lambda: {
#         "BLOG_ID": "id",
#         "BASE_URL": "url/",
#         "LABELS": "labels",
#         "LOCATION_JSON": '{}',
#         "LIVE_POST": True,
#         "FILE_EXTENSION": "html",
#         "MODEL_NAME": "llama3.1",
#         "MODEL_OPTIONS_JSON": '{}',
#         "TOPIC": "topic",
#         "SYSTEM_PROMPT_ROLE": "role",
#         "SYSTEM_PROMPT_STYLE": "style",
#         "SYSTEM_PROMPT_TEMPLATE": "{SYSTEM_PROMPT_ROLE} {SYSTEM_PROMPT_STYLE}",
#         "USER_PROMPT_TEMPLATE": "{TOPIC} {SYSTEM_PROMPT_STYLE}",
#         "FILTER_POST_COUNT": 1,
#         "FILTER_POST": False,
#         "FILTER_DAYS": 1,
#         "STREAM": "False",
#     })
@patch('affiliate_mktg.src.blog.blog_manager.configValues', new={
    "BLOG_ID": "id",
    "BASE_URL": "url/",
    "LABELS": "labels",
    "LOCATION_JSON": '{}',
    "LIVE_POST": True,
    "FILE_EXTENSION": "html",
    "MODEL_NAME": "llama3.1",
    "MODEL_OPTIONS_JSON": '{}',
    "TOPIC": "topic",
    "SYSTEM_PROMPT_ROLE": "role",
    "SYSTEM_PROMPT_STYLE": "style",
    "SYSTEM_PROMPT_TEMPLATE": "{SYSTEM_PROMPT_ROLE} {SYSTEM_PROMPT_STYLE}",
    "USER_PROMPT_TEMPLATE": "{TOPIC} {SYSTEM_PROMPT_STYLE}",
    "FILTER_POST_COUNT": 1,
    "FILTER_POST": False,
    "FILTER_DAYS": 1,
    "STREAM": "False",
},)

@patch('affiliate_mktg.src.blog.blog_manager.BlogService')
@patch('affiliate_mktg.src.blog.blog_manager.BlogGenerator')
def test_blog_manager_init(mock_gen, mock_service, monkeypatch):
    mgr = bm.BlogManager()
    assert mgr.BLOG_ID == "id"
    assert mgr.blogService is mock_service.return_value
    assert mgr.blogGenerator is mock_gen.return_value

@patch('affiliate_mktg.src.blog.blog_manager.BlogService')
def test_initialize_service_success(mock_service):
    mgr = bm.BlogManager()
    mock_service.return_value.get_blogger_service.return_value = 'svc'
    assert mgr._initialize_service() == 'svc'

@patch('affiliate_mktg.src.blog.blog_manager.BlogService')
def test_initialize_service_import_error(mock_service):
    mgr = bm.BlogManager()
    mock_service.return_value.get_blogger_service.side_effect = ImportError('fail')
    assert mgr._initialize_service() is None

@patch('affiliate_mktg.src.blog.blog_manager.BlogManager._initialize_service', return_value=MagicMock())
def test_get_blog_all_posts_success(mock_init):
    mgr = bm.BlogManager()
    service = mock_init.return_value
    user = {'displayName': 'User'}
    service.users.return_value.get.return_value.execute.return_value = user
    service.posts.return_value.list.return_value.execute.return_value = {"items": []}
    service.posts.return_value.list_next.return_value = None
    import asyncio
    result = asyncio.get_event_loop().run_until_complete(mgr.get_blog_all_posts(1))
    assert result == []

@patch('affiliate_mktg.src.blog.blog_manager.BlogManager._initialize_service', side_effect=Exception('fail'))
def test_get_blog_all_posts_exception(mock_init):
    mgr = bm.BlogManager()
    import asyncio
    result = asyncio.get_event_loop().run_until_complete(mgr.get_blog_all_posts(1))
    assert result is None

@patch('affiliate_mktg.src.blog.blog_manager.BlogManager._initialize_service', return_value=MagicMock())
def test_post_blog_empty_content(mock_init):
    mgr = bm.BlogManager()
    import asyncio
    result = asyncio.get_event_loop().run_until_complete(mgr._post_blog('', 'topic', 'url', 'labels', 'loc', True))
    assert result is None

@patch('affiliate_mktg.src.blog.blog_manager.BlogManager._initialize_service', return_value=MagicMock())
def test_post_blog_success(mock_init):
    mgr = bm.BlogManager()
    import asyncio
    result = asyncio.get_event_loop().run_until_complete(mgr._post_blog('content', 'topic', 'url', 'labels', 'loc', True))
    assert result is None

@pytest.mark.asyncio
async def test_clean_blog_post_and_beautify(monkeypatch):
    mgr = bm.BlogManager()
    # Clean blog post with doctype
    blog_post = '<!DOCTYPE html>\n<html>content</html>'
    result = await mgr._clean_blog_post(blog_post)
    assert '<!DOCTYPE html>' in result
    # Clean blog post with missing doctype
    blog_post2 = '<html>content</html>'
    result2 = await mgr._clean_blog_post(blog_post2)
    assert '<!DOCTYPE html>' in result2
    # Beautify
    monkeypatch.setattr('affiliate_mktg.src.blog.blog_manager.BeautifulSoup', MagicMock(return_value=MagicMock(find=MagicMock(return_value=None), prettify=lambda: 'pretty')))
    result3 = await mgr._beautify_html_blog_post('<html></html>', 'post', 'img')
    assert result3 == 'pretty'

@pytest.mark.asyncio
async def test_is_valid_HTML_tag():
    mgr = bm.BlogManager()
    assert mgr._is_valid_HTML_tag('<html></html>') is True
    assert mgr._is_valid_HTML_tag('<html>') is True

@pytest.mark.asyncio
async def test_generate_blog_post(monkeypatch):
    mgr = bm.BlogManager()
    monkeypatch.setattr(mgr.blogGenerator, 'generate_blog_by_model', AsyncMock(return_value='blog'))
    result = await mgr._generate_blog_post('sys', 'user', 'llama3.1', {})
    assert result == 'blog'

@pytest.mark.asyncio
async def test_generate_blog_post_stream(monkeypatch):
    mgr = bm.BlogManager()
    monkeypatch.setattr(mgr.blogGenerator, 'generate_blog_by_model_stream', AsyncMock(return_value='blog'))
    result = await mgr._generate_blog_post_stream('sys', 'user', 'llama3.1', {})
    assert result == 'blog'
