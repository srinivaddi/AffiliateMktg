import json
from pathlib import Path

from affiliate_mktg.src.core.models import SearchIndex
from affiliate_mktg.src.utils.logging_setup import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class SearchIndexManager:
    def __init__(self, search_index_path: str | None = None):
        logger.info("affiliate marketing search index ...")
        self._search_index_path = search_index_path or "search_index.json"

    def _resolve_path(self) -> Path:
        p = Path(self._search_index_path)
        if not p.is_absolute():
            p = Path.cwd() / p
        return p

    async def generate_search_index_async(self) -> list:
        return await self.generate_search_index()

    def generate_search_index(self) -> list:
        path = self._resolve_path()
        with open(path, "r", encoding="utf-8") as f:
            search_indexes = json.load(f)

        search_index_collection = []
        for entry in search_indexes:
            keywords = list(entry["Keywords"])
            search_index_collection.append(
                SearchIndex(
                    search_index=entry["SearchIndex"],
                    display_name=entry["DisplayName"],
                    keywords=keywords,
                )
            )
        return search_index_collection
