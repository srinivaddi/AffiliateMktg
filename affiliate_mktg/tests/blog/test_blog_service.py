import pytest
from unittest.mock import patch, MagicMock
from affiliate_mktg.src.blog.blog_service import BlogService
import affiliate_mktg.src.blog.blog_service as bs

@patch('affiliate_mktg.src.blog.blog_service.configValues', new={
    "SCOPES_STR": "scope",
    "SCOPES": "scope",
    "SERVICE_NAME": "service",
    "SERVICE_VERSION": "v1",
    "CLIENT_SECRETS_JSON": "{}",
})

def test_blog_service_init():
    service = bs.BlogService()
    assert service.SCOPES == ["scope"]
    assert service.SERVICE_NAME == "service"
    assert service.SERVICE_VERSION == "v1"
    assert service.CLIENT_SECRETS == {}
    
@patch('affiliate_mktg.src.blog.blog_service.pickle')
@patch('affiliate_mktg.src.blog.blog_service.os.path.exists', return_value=True)
@patch('affiliate_mktg.src.blog.blog_service.open', create=True)
@patch('affiliate_mktg.src.blog.blog_service.get_blog_config', return_value={
    "SCOPES_STR": "scope",
    "SERVICE_NAME": "service",
    "SERVICE_VERSION": "v1",
    "CLIENT_SECRETS_JSON": '{}',
})
def test_get_credentials_valid(mock_config, mock_open, mock_exists, mock_pickle):
    service = bs.BlogService()
    creds = MagicMock()
    creds.valid = True
    mock_pickle.load.return_value = creds
    mock_open().__enter__ = lambda s: s
    mock_open().__exit__ = lambda s, exc_type, exc_val, exc_tb: None
    result = service.get_credentials()
    assert result is creds

@patch('affiliate_mktg.src.blog.blog_service.pickle')
@patch('affiliate_mktg.src.blog.blog_service.os.path.exists', return_value=False)
@patch('affiliate_mktg.src.blog.blog_service.open', create=True)
@patch('affiliate_mktg.src.blog.blog_service.get_blog_config', return_value={
    "SCOPES_STR": "scope",
    "SERVICE_NAME": "service",
    "SERVICE_VERSION": "v1",
    "CLIENT_SECRETS_JSON": '{}',
})
def test_get_credentials_exception(mock_config, mock_open, mock_exists, mock_pickle):
    service = bs.BlogService()
    mock_pickle.load.side_effect = Exception('fail')
    with pytest.raises(ValueError):
        service.get_credentials()

@patch('affiliate_mktg.src.blog.blog_service.build')
@patch('affiliate_mktg.src.blog.blog_service.configValues', new={
    "SCOPES_STR": "scope",
    "SERVICE_NAME": "service",
    "SERVICE_VERSION": "v1",
    "CLIENT_SECRETS_JSON": '{}',
})
def test_get_credentials_exception(mock_build):
    fake_creds = MagicMock(name="Credentials")
    with patch.object(bs.BlogService, "get_credentials", return_value=fake_creds):
        mock_build.return_value = "service"
        service = bs.BlogService()
        result = service.get_blogger_service()
        assert result == "service"
        mock_build.assert_called_once_with(
            "service", "v1", credentials=fake_creds
        )

@patch('affiliate_mktg.src.blog.blog_service.BlogService.get_credentials', side_effect=Exception('fail'))
@patch('affiliate_mktg.src.blog.blog_service.configValues', new={
    "SCOPES_STR": "scope",
    "SERVICE_NAME": "service",
    "SERVICE_VERSION": "v1",
    "CLIENT_SECRETS_JSON": '{}',
})
def test_get_blogger_service_exception(mock_get_credentials):
    service = bs.BlogService()
    with pytest.raises(ValueError):
        service.get_blogger_service()