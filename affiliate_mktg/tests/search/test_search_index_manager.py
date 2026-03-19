import json
import sys
import types
import importlib
from pathlib import Path

import pytest

pytestmark = pytest.mark.asyncio

# ✅ Update if your module path is different
MODULE_UNDER_TEST = "affiliate_mktg.src.search.search_index_manager"


def _install_stub_module(monkeypatch, full_name: str, **attrs):
    """
    Install a stub module into sys.modules (and ensure parent packages exist).
    Used to neutralize logging side effects at import time.
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
def search_index_manager_module(monkeypatch):
    """Import module under test with logging safely stubbed."""
    class DummyLogger:
        def info(self, *args, **kwargs): pass
        def error(self, *args, **kwargs): pass

    _install_stub_module(
        monkeypatch,
        "affiliate_mktg.src.utils.logging_setup",
        setup_logging=lambda: None,
        get_logger=lambda name=None: DummyLogger(),
    )

    if MODULE_UNDER_TEST in sys.modules:
        del sys.modules[MODULE_UNDER_TEST]

    return importlib.import_module(MODULE_UNDER_TEST)


# -----------------------------
# Helper: write sample JSON
# -----------------------------

def write_search_index_json(path: Path):
    data = [
        {
            "SearchIndex": "Books",
            "DisplayName": "Books",
            "Keywords": ["fiction", "novel", "literature"],
        },
        {
            "SearchIndex": "Electronics",
            "DisplayName": "Electronics",
            "Keywords": ["headphones", "speaker"],
        },
    ]
    path.write_text(json.dumps(data), encoding="utf-8")


# -----------------------------
# Tests
# -----------------------------

def test_resolve_path_relative(search_index_manager_module, tmp_path, monkeypatch):
    SearchIndexManager = search_index_manager_module.SearchIndexManager

    monkeypatch.chdir(tmp_path)

    mgr = SearchIndexManager(search_index_path="search_index.json")
    resolved = mgr._resolve_path()

    assert resolved == tmp_path / "search_index.json"
    assert isinstance(resolved, Path)


def test_resolve_path_absolute(search_index_manager_module, tmp_path):
    SearchIndexManager = search_index_manager_module.SearchIndexManager

    abs_path = tmp_path / "search_index.json"
    mgr = SearchIndexManager(search_index_path=str(abs_path))

    resolved = mgr._resolve_path()

    assert resolved == abs_path
    assert resolved.is_absolute()


def test_generate_search_index_reads_and_maps(search_index_manager_module, tmp_path, monkeypatch):
    SearchIndexManager = search_index_manager_module.SearchIndexManager
