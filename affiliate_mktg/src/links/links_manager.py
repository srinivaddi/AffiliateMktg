import asyncio

from affiliate_mktg.src.links.links_generator import LinksGenerator
from affiliate_mktg.src.blog.blog_manager import BlogManager
from affiliate_mktg.src.core.models import BlogInputConfig, SearchInput
from affiliate_mktg.src.utils.common import to_camel_case
from affiliate_mktg.src.search.search_index_manager import SearchIndexManager
from affiliate_mktg.src.utils.logging_setup import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class LinksManager:
    def __init__(self):
        logger.info("Hello from affiliate marketing link generation manager...")
        self.linksGenerator = LinksGenerator()
        self.blogManager = BlogManager()
        self.searchIndexManager = SearchIndexManager()

    async def generate_link_post_blog(self, searchInput: SearchInput):
        items = await self.generate_link(searchInput)
        if items and len(items) > 0:
            await self.post_link_blog(items)

    async def generate_link(self, searchInput: SearchInput):
        items = await self.linksGenerator.generate_link(searchInput)
        return items

    async def post_link_blog(self, items):
        for item in items:
            logger.info(f"Generated Link: {item}")

            blogInputConfig = BlogInputConfig(
                items_arg=item,
                topic_arg=item.short_display_value,
                topic_arg_post=item.detail_page_url,
                topicurl_arg=to_camel_case(item.short_display_value)
                .lower()
                .replace(" ", "-"),
                labels_arg="Affiliate Marketing",
                systempromptrole_arg="Affiliate Marketing Blogger",
                systempromptstyle_arg="Professional Affiliate Marketing",
            )
            await self.blogManager.generate_blog_post_blogger(blogInputConfig)

    async def generate_link_post_blog_manual(self, searchInput: SearchInput):
        items = []
        try:
            items = await self.generate_link_manual(searchInput)
            if items and len(items) > 0:
                tasks = [
                    self.post_link_blog_manual(item) for item in items
                ]
                results = await asyncio.gather(*tasks)

                logger.info("\nAll items processed. Results:")
                for result in results:
                    logger.info(result)

                total_item_count = searchInput.item_count
                item_success = sum(1 for r in results if r[0] is True)
                item_failure = len(results) - item_success

                if item_success == total_item_count:
                    content_str = f"Amazon Affiliate marketing links Generation and posting success for all {total_item_count} items out of {total_item_count} totals items."
                elif item_failure == total_item_count:
                    content_str = f"Amazon Affiliate marketing links Generation and posting failure for all {item_failure} items out of {total_item_count} totals items. All items were filtered becasue of filter used."
                else:
                    content_str = f"Amazon Affiliate marketing links Generation and posting success for {item_success} items and failure for {item_failure} items out of {total_item_count} items. Some items were filtered becasue of filter used."

                return {
                    "status": "Processed",
                    "count": total_item_count,
                    "results": results,
                    "success": True,
                    "content": content_str,
                }
            else:
                logger.info("\nNo items processed.")
                return {
                    "status": "Not Processed",
                    "count": 0,
                    "results": None,
                    "success": False,
                    "content": "Amazon Affiliate marketing links NOT Generated and Posted as 0 links were processed.",
                }

        except Exception as e:
            logger.error(
                f"An error occurred while generating and posting amazon affiliate marketing links: {e}",
                exc_info=True,
            )
            return {
                "status": "Failure",
                "count": len(items),
                "results": str(e),
                "success": False,
                "content": "Amazon Affiliate marketing links NOT Generated and Posted becasue of error.",
            }

    async def generate_link_manual(self, searchInput: SearchInput):
        try:
            logger.info(
                f"Generating {searchInput.item_count} Link for keywords: {searchInput.keywords} search_index {searchInput.search_index}"
            )
            items = await self.linksGenerator.generate_link(searchInput)
            return items
        except Exception as e:
            logger.error(
                f"An error occurred while generating amazon affiliate marketing links: {e}",
                exc_info=True,
            )
            raise ValueError(
                f"An error occurred while generating amazon affiliate marketing links: {e}"
            )

    async def post_link_blog_manual(self, item):
        try:
            logger.info(f"Posting link for {item.short_display_value}")
            logger.info(f"Posting link for {item.asin}")

            blogInputConfig = BlogInputConfig(
                items_arg=item,
                topic_arg=item.short_display_value,
                topic_arg_post=item.detail_page_url,
                topicurl_arg=to_camel_case(item.short_display_value)
                .lower()
                .replace(" ", "-"),
                labels_arg="Affiliate Marketing",
                systempromptrole_arg="Affiliate Marketing Blogger",
                systempromptstyle_arg="Professional Affiliate Marketing",
            )
            return await self.blogManager.generate_blog_post_blogger(blogInputConfig)
        except Exception as e:
            logger.error(
                f"An error occurred while posting amazon affiliate marketing links to blog: {e}",
                exc_info=True,
            )
            raise ValueError(
                f"An error occurred while posting amazon affiliate marketing links to blog: {e}"
            )
