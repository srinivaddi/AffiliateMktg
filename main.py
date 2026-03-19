import asyncio

from affiliate_mktg.src.links.links_manager import LinksManager
from affiliate_mktg.src.core.models import SearchInput
from affiliate_mktg.src.core.enums import AvailabilityType
from affiliate_mktg.src.utils.logging_setup import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

class MainApp:
    def __init__(self):
        logger.info("affiliate marketing main ...")
        self.linksManager = LinksManager()

    async def main(self):
        logger.info("Starting affiliate marketing link generation...")

        searchInput = SearchInput(
            keywords="washers",
            search_index="Appliances",
            item_count=1,
            show_availability_type=[AvailabilityType.INSTOCK.value, AvailabilityType.INSTOCKSCARCE.value],
            show_prime_delivery_items=False,
            show_isprimeexclusive_items=False,
            show_isbuyboxwinner_items=False,
            show_freeshipping_items=False,
            show_discount_items=False,
            discount_percentage=0,
        )
        await self.linksManager.generate_link_post_blog(searchInput)

        logger.info("Process completed.")


if __name__ == "__main__":
    app = MainApp()
    asyncio.run(app.main())
