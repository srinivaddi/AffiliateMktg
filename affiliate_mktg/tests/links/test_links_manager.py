import sys
import types
import importlib
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.asyncio

# ✅ Change if your LinksManager module path is different
MODULE_UNDER_TEST = "affiliate_mktg.src.links.links_manager"


def _install_stub_module(monkeypatch, full_name: str, **attrs):
    """
    Install a stub module into sys.modules (and ensure parent packages exist).
    Useful to avoid import-time side effects and heavy dependencies.
    """
    parts = full_name.split(".")
    for i in range(1, len(parts) + 1):
        name = ".".join(parts[:i])
        if name not in sys.modules:
            mod = types.ModuleType(name)
            monkeypatch.setitem(sys.modules, name, mod)

    mod = sys.modules[full_name]
    for k, v in attrs.items():
        setattr(mod, k, v)
    return mod


@pytest.fixture
def links_manager_module(monkeypatch):
    """
    Safely import module under test by stubbing logging setup (import side effects).
    We do NOT stub internal project modules unless needed; we override dependencies
    on the LinksManager instance itself in tests.
    """
    class DummyLogger:
        def info(self, *args, **kwargs): pass
        def error(self, *args, **kwargs): pass

    _install_stub_module(
        monkeypatch,
        "affiliate_mktg.src.utils.logging_setup",
        setup_logging=lambda: None,
        get_logger=lambda name=None: DummyLogger(),
    )

    # If your project doesn't include to_camel_case in test env, uncomment this stub:
    # _install_stub_module(
    #     monkeypatch,
    #     "affiliate_mktg.src.utils.common",
    #     to_camel_case=lambda s: s,
    # )

    # Import fresh each time
    if MODULE_UNDER_TEST in sys.modules:
        del sys.modules[MODULE_UNDER_TEST]

    return importlib.import_module(MODULE_UNDER_TEST)


# -----------------------
# Simple fakes / helpers
# -----------------------

class FakeLinksGenerator:
    def __init__(self, items=None, exc=None):
        self._items = items if items is not None else []
        self._exc = exc
        self.calls = []

    async def generate_link(self, search_input):
        self.calls.append(search_input)
        if self._exc:
            raise self._exc
        return self._items


class FakeBlogManager:
    def __init__(self, results=None, exc=None):
        # results: return value per call (if list, pop in order)
        self._results = results
        self._exc = exc
        self.calls = []  # list of BlogInputConfig passed in

    async def generate_blog_post_blogger(self, blog_input_config):
        self.calls.append(blog_input_config)
        if self._exc:
            raise self._exc
        if isinstance(self._results, list):
            return self._results.pop(0)
        return self._results


class FakeSearchIndexManager:
    pass


def make_item(short="Echo Dot", url="https://amazon.com/dp/B000", asin="B000"):
    # minimal item interface used by LinksManager
    return SimpleNamespace(
        short_display_value=short,
        detail_page_url=url,
        asin=asin,
    )


def make_search_input(module, item_count=2, keywords="k", search_index="idx"):
    # If your project provides SearchInput dataclass, this will use it.
    # Otherwise you can replace with SimpleNamespace matching attributes.
    SearchInput = module.SearchInput
    return SearchInput(
        keywords=keywords,
        search_index=search_index,
        item_count=item_count,
        show_availability_type=[],
        show_prime_delivery_items=False,
        show_isprimeexclusive_items=False,
        show_isbuyboxwinner_items=False,
        show_freeshipping_items=False,
        show_discount_items=False,
        discount_percentage=0,
    )

async def test_generate_link_delegates(links_manager_module, monkeypatch):
    LinksManager = links_manager_module.LinksManager

    mgr = LinksManager()
    fake_items = [make_item(short="A"), make_item(short="B")]
    mgr.linksGenerator = FakeLinksGenerator(items=fake_items)

    search = make_search_input(links_manager_module, item_count=2)
    items = await mgr.generate_link(search)

    assert items == fake_items
    assert mgr.linksGenerator.calls == [search]


async def test_generate_link_post_blog_calls_post_when_items_exist(links_manager_module, monkeypatch):
    LinksManager = links_manager_module.LinksManager

    mgr = LinksManager()
    items = [make_item(short="A"), make_item(short="B")]

    async def fake_generate_link(si):
        return items

    called = {"count": 0}

    async def fake_post_link_blog(_items):
        called["count"] += 1
        assert _items == items

    monkeypatch.setattr(mgr, "generate_link", fake_generate_link)
    monkeypatch.setattr(mgr, "post_link_blog", fake_post_link_blog)

    search = make_search_input(links_manager_module, item_count=2)
    await mgr.generate_link_post_blog(search)

    assert called["count"] == 1


async def test_generate_link_post_blog_skips_when_no_items(links_manager_module, monkeypatch):
    LinksManager = links_manager_module.LinksManager

    mgr = LinksManager()

    async def fake_generate_link(si):
        return []

    called = {"count": 0}

    async def fake_post_link_blog(_items):
        called["count"] += 1

    monkeypatch.setattr(mgr, "generate_link", fake_generate_link)
    monkeypatch.setattr(mgr, "post_link_blog", fake_post_link_blog)

    search = make_search_input(links_manager_module, item_count=2)
    await mgr.generate_link_post_blog(search)

    assert called["count"] == 0


async def test_post_link_blog_builds_blog_input_config_per_item(links_manager_module, monkeypatch):
    LinksManager = links_manager_module.LinksManager

    mgr = LinksManager()
    mgr.blogManager = FakeBlogManager(results="ok")

    # Make to_camel_case deterministic for this test
    monkeypatch.setattr(links_manager_module, "to_camel_case", lambda s: "Camel Case Value")

    items = [make_item(short="Echo Dot", url="https://amazon.com/dp/ECHO", asin="ECHO")]

    await mgr.post_link_blog(items)

    assert len(mgr.blogManager.calls) == 1
    cfg = mgr.blogManager.calls[0]

    # Validate BlogInputConfig fields
    assert cfg.items_arg.asin == "ECHO"
    assert cfg.topic_arg == "Echo Dot"
    assert cfg.topic_arg_post == "https://amazon.com/dp/ECHO"
    assert cfg.topicurl_arg == "camel-case-value"  # lower + replace(" ", "-")
    assert cfg.labels_arg == "Affiliate Marketing"
    assert cfg.systempromptrole_arg == "Affiliate Marketing Blogger"
    assert cfg.systempromptstyle_arg == "Professional Affiliate Marketing"


async def test_generate_link_manual_returns_items(links_manager_module):
    LinksManager = links_manager_module.LinksManager

    mgr = LinksManager()
    fake_items = [make_item(short="A")]
    mgr.linksGenerator = FakeLinksGenerator(items=fake_items)

    search = make_search_input(links_manager_module, item_count=1)
    items = await mgr.generate_link_manual(search)

    assert items == fake_items


async def test_generate_link_manual_wraps_exception_as_valueerror(links_manager_module):
    LinksManager = links_manager_module.LinksManager

    mgr = LinksManager()
    mgr.linksGenerator = FakeLinksGenerator(exc=RuntimeError("boom"))

    search = make_search_input(links_manager_module, item_count=1)

    with pytest.raises(ValueError) as e:
        await mgr.generate_link_manual(search)

    assert "An error occurred while generating amazon affiliate marketing links" in str(e.value)


async def test_post_link_blog_manual_returns_blog_manager_result(links_manager_module, monkeypatch):
    LinksManager = links_manager_module.LinksManager

    mgr = LinksManager()
    mgr.blogManager = FakeBlogManager(results=("ok", "url"))

    monkeypatch.setattr(links_manager_module, "to_camel_case", lambda s: "X Y")

    item = make_item(short="Echo Dot", url="https://amazon.com/dp/ECHO", asin="ECHO")
    result = await mgr.post_link_blog_manual(item)

    assert result == ("ok", "url")
    assert len(mgr.blogManager.calls) == 1
    assert mgr.blogManager.calls[0].topicurl_arg == "x-y"


async def test_post_link_blog_manual_wraps_exception_as_valueerror(links_manager_module):
    LinksManager = links_manager_module.LinksManager

    mgr = LinksManager()
    mgr.blogManager = FakeBlogManager(exc=RuntimeError("fail"))

    item = make_item(short="Echo Dot", url="u", asin="a")

    with pytest.raises(ValueError) as e:
        await mgr.post_link_blog_manual(item)

    assert "An error occurred while posting amazon affiliate marketing links to blog" in str(e.value)


async def test_generate_link_post_blog_manual_all_success(links_manager_module, monkeypatch):
    LinksManager = links_manager_module.LinksManager
    mgr = LinksManager()

    items = [make_item(short="A"), make_item(short="B")]
    search = make_search_input(links_manager_module, item_count=2)

    async def fake_generate_link_manual(si):
        return items

    async def fake_post_link_blog_manual(item):
        return (True, item.asin)

    monkeypatch.setattr(mgr, "generate_link_manual", fake_generate_link_manual)
    monkeypatch.setattr(mgr, "post_link_blog_manual", fake_post_link_blog_manual)

    result = await mgr.generate_link_post_blog_manual(search)

    assert result["status"] == "Processed"
    assert result["count"] == 2
    assert result["success"] is True
    assert "success for all 2 items" in result["content"]
    assert result["results"] == [(True, "B000"), (True, "B000")] or len(result["results"]) == 2  # asin default may match


async def test_generate_link_post_blog_manual_all_failure(links_manager_module, monkeypatch):
    LinksManager = links_manager_module.LinksManager
    mgr = LinksManager()

    items = [make_item(short="A"), make_item(short="B")]
    search = make_search_input(links_manager_module, item_count=2)

    async def fake_generate_link_manual(si):
        return items

    async def fake_post_link_blog_manual(item):
        return (False, "filtered")

    monkeypatch.setattr(mgr, "generate_link_manual", fake_generate_link_manual)
    monkeypatch.setattr(mgr, "post_link_blog_manual", fake_post_link_blog_manual)

    result = await mgr.generate_link_post_blog_manual(search)

    assert result["status"] == "Processed"
    assert result["count"] == 2
    assert result["success"] is True
    assert "failure for all" in result["content"]
    assert result["results"] == [(False, "filtered"), (False, "filtered")]


async def test_generate_link_post_blog_manual_partial_success(links_manager_module, monkeypatch):
    LinksManager = links_manager_module.LinksManager
    mgr = LinksManager()

    items = [make_item(short="A", asin="A"), make_item(short="B", asin="B")]
    search = make_search_input(links_manager_module, item_count=2)

    async def fake_generate_link_manual(si):
        return items

    async def fake_post_link_blog_manual(item):
        return (item.asin == "A", item.asin)

    monkeypatch.setattr(mgr, "generate_link_manual", fake_generate_link_manual)
    monkeypatch.setattr(mgr, "post_link_blog_manual", fake_post_link_blog_manual)

    result = await mgr.generate_link_post_blog_manual(search)

    assert result["status"] == "Processed"
    assert result["count"] == 2
    assert result["success"] is True
    assert "success for 1 items and failure for 1 items" in result["content"]
    assert result["results"] == [(True, "A"), (False, "B")]


async def test_generate_link_post_blog_manual_no_items_processed(links_manager_module, monkeypatch):
    LinksManager = links_manager_module.LinksManager
    mgr = LinksManager()

    search = make_search_input(links_manager_module, item_count=2)

    async def fake_generate_link_manual(si):
        return []

    monkeypatch.setattr(mgr, "generate_link_manual", fake_generate_link_manual)

    result = await mgr.generate_link_post_blog_manual(search)

    assert result["status"] == "Not Processed"
    assert result["count"] == 0
    assert result["success"] is False
    assert "0 links were processed" in result["content"]


async def test_generate_link_post_blog_manual_exception_path(links_manager_module, monkeypatch):
    LinksManager = links_manager_module.LinksManager
    mgr = LinksManager()

    search = make_search_input(links_manager_module, item_count=2)

    async def fake_generate_link_manual(si):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(mgr, "generate_link_manual", fake_generate_link_manual)

    result = await mgr.generate_link_post_blog_manual(search)

    assert result["status"] == "Failure"
    assert result["success"] is False
    assert "NOT Generated and Posted becasue of error" in result["content"]
    assert "kaboom" in result["results"]