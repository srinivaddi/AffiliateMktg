import json
import sys
import types
import importlib
from types import SimpleNamespace
import pytest

MODULE_UNDER_TEST = "affiliate_mktg.src.links.links_generator"

def _install_stub_module(monkeypatch, full_name: str, **attrs):
    """
    Install a stub module into sys.modules (and ensure parent packages exist).
    This lets us import the module under test without having real external deps installed.
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
def links_module(monkeypatch):
    """
    Import the module under test safely by stubbing:
    - creatorsapi_python_sdk + submodules
    - amazon_creatorsapi
    - affiliate_mktg.src.config.amazon_loader.get_amazon_config
    - affiliate_mktg.src.utils.logging_setup.setup_logging/get_logger
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

    _install_stub_module(
        monkeypatch,
        "affiliate_mktg.src.config.amazon_loader",
        get_amazon_config=lambda: {
            "CREDENTIAL_ID_CREATORSAPI": "id",
            "CREDENTIAL_SECRET_CREATORSAPI": "secret",
            "VERSION_CREATORSAPI": "v",
            "PARTNER_TAG": "tag",
            "ENCRYPTION_KEY": "enc",
            "MARKETPLACE": "US",
            "THROTTLE_DELAY": 0,
            "HOST": "host",
            "REGION": "region",
        },
    )

    class ApiException(Exception):
        def __init__(self, status=500, body="boom", headers=None):
            super().__init__("ApiException")
            self.status = status
            self.body = body
            self.headers = headers or {"x-amzn-RequestId": "reqid"}

    class SearchItemsResource:
        IMAGES_DOT_PRIMARY_DOT_LARGE = "IMAGES.PRIMARY.LARGE"
        ITEM_INFO_DOT_TITLE = "ITEM_INFO.TITLE"
        OFFERS_V2_DOT_LISTINGS_DOT_AVAILABILITY = "OFFERS.LISTINGS.AVAILABILITY"
        OFFERS_V2_DOT_LISTINGS_DOT_CONDITION = "OFFERS.LISTINGS.CONDITION"
        OFFERS_V2_DOT_LISTINGS_DOT_DEAL_DETAILS = "OFFERS.LISTINGS.DEAL_DETAILS"
        OFFERS_V2_DOT_LISTINGS_DOT_IS_BUY_BOX_WINNER = "OFFERS.LISTINGS.BUY_BOX"
        OFFERS_V2_DOT_LISTINGS_DOT_LOYALTY_POINTS = "OFFERS.LISTINGS.LOYALTY"
        OFFERS_V2_DOT_LISTINGS_DOT_MERCHANT_INFO = "OFFERS.LISTINGS.MERCHANT"
        OFFERS_V2_DOT_LISTINGS_DOT_PRICE = "OFFERS.LISTINGS.PRICE"
        OFFERS_V2_DOT_LISTINGS_DOT_TYPE = "OFFERS.LISTINGS.TYPE"

    _install_stub_module(monkeypatch, "creatorsapi_python_sdk")
    _install_stub_module(monkeypatch, "creatorsapi_python_sdk.models.search_items_request_content",
                         SearchItemsRequestContent=object)
    _install_stub_module(monkeypatch, "creatorsapi_python_sdk.models.search_items_resource",
                         SearchItemsResource=SearchItemsResource)
    _install_stub_module(monkeypatch, "creatorsapi_python_sdk.rest", ApiException=ApiException)

    class Country:
        US = "US"

    class AmazonCreatorsApi:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def search_items(self, **kwargs):
            raise NotImplementedError("tests should patch this")

    _install_stub_module(monkeypatch, "amazon_creatorsapi",
                         AmazonCreatorsApi=AmazonCreatorsApi, Country=Country)

    # Ensure we import fresh
    if MODULE_UNDER_TEST in sys.modules:
        del sys.modules[MODULE_UNDER_TEST]

    mod = importlib.import_module(MODULE_UNDER_TEST)
    return mod

class ItemsContainer:
    """Behaves like response.items in your code: iterable + .count"""
    def __init__(self, items):
        self._items = list(items)

    @property
    def count(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)


def make_fake_sdk_item(
    asin="B000123",
    url="https://amazon.com/dp/B000123",
    title="My Product: Deluxe, Edition",
    image_large=("https://img/large.jpg", 1000, 1000),
    image_medium=("https://img/med.jpg", 500, 500),
    image_small=("https://img/small.jpg", 100, 100),
    availability_type="AVAILABLE",
    is_buy_box=True,
    price_amount=99.99,
    price_display="99.99",
    price_currency="USD",
    savings_amount=20.0,
    savings_display="20.00",
    savings_currency="USD",
    savings_percentage=20,
    deal_access_type="ALL",
    prime_eligible=True,
    free_shipping=True,
):
    # Images nesting: itm.images.primary.large.height, etc.
    large = SimpleNamespace(url=image_large[0], height=image_large[1], width=image_large[2]) if image_large else None
    medium = SimpleNamespace(url=image_medium[0], height=image_medium[1], width=image_medium[2]) if image_medium else None
    small = SimpleNamespace(url=image_small[0], height=image_small[1], width=image_small[2]) if image_small else None
    images = SimpleNamespace(primary=SimpleNamespace(large=large, medium=medium, small=small))

    # Title nesting: itm.item_info.title.display_value
    item_info = SimpleNamespace(title=SimpleNamespace(display_value=title))

    # Listing nesting: offers_v2.listings[*]
    money = SimpleNamespace(amount=price_amount, display_amount=price_display, currency=price_currency)
    savings_money = SimpleNamespace(amount=savings_amount, display_amount=savings_display, currency=savings_currency)
    savings = SimpleNamespace(money=savings_money, percentage=savings_percentage)
    price = SimpleNamespace(money=money, savings=savings)

    availability = SimpleNamespace(
        max_order_quantity="10",
        min_order_quantity="1",
        message="In stock",
        type=availability_type,
    )

    deal_details = SimpleNamespace(access_type=deal_access_type)

    listing = SimpleNamespace(
        condition="New",
        is_buy_box_winner=is_buy_box,
        price=price,
        availability=availability,
        deal_details=deal_details,
        # other attributes exist in resources but not used by your mapping
    )

    offers_v2 = SimpleNamespace(listings=[listing])

    return SimpleNamespace(
        asin=asin,
        detail_page_url=url,
        images=images,
        item_info=item_info,
        offers_v2=offers_v2,
    )


pytestmark = pytest.mark.asyncio

async def test_filter_param_item_true_when_no_listings_and_no_discount(links_module):
    LinksGenerator = links_module.LinksGenerator
    from affiliate_mktg.src.core.models import Item, Offers, SearchInput

    lg = LinksGenerator()

    item = Item(
        asin="A",
        detail_page_url="u",
        short_display_value="s",
        display_value="d",
        offers=Offers(listings=[]),
        images=[],
    )
    search = SearchInput(
        keywords="k",
        search_index="idx",
        item_count=1,
        show_availability_type=[],
        show_prime_delivery_items=False,
        show_isprimeexclusive_items=False,
        show_isbuyboxwinner_items=False,
        show_freeshipping_items=False,
        show_discount_items=False,
        discount_percentage=0,
    )

    assert await lg.filter_param_item(search, item, show_discount_items=False, discount_percentage=0) is True


async def test_filter_param_item_availability_filter_passes(links_module):
    LinksGenerator = links_module.LinksGenerator
    from affiliate_mktg.src.core.models import (
        Item, Offers, Listing, Availability, DeliveryInfo, ProgramEligibility, Price, Savings, SearchInput
    )

    class DummyAvail:
        value = "AVAILABLE"

    lg = LinksGenerator()

    listing = Listing(
        condition=1,
        id="1",
        isBuyBoxWinner=False,
        availability=Availability(maxOrderQuantity="1", message="ok", minOrderQuantity="1", type="AVAILABLE"),
        deliveryInfo=DeliveryInfo(isAmazonFulfilled=False, isFreeShippingEligible=False, isPrimeEligible=False, shippingCharges=""),
        programEligibility=ProgramEligibility(isAll=False, isPrimeExclusive=False, isPrimeEarlyAccess=False),
        price=Price(amount=10.0, currency="USD", display_amount=10.0, savings=Savings(amount=0, currency="USD", display_amount=0, percentage=0)),
    )

    item = Item(
        asin="A",
        detail_page_url="u",
        short_display_value="s",
        display_value="d",
        offers=Offers(listings=[listing]),
        images=[],
    )

    search = SearchInput(
        keywords="k",
        search_index="idx",
        item_count=1,
        show_availability_type=[DummyAvail()],
        show_prime_delivery_items=False,
        show_isprimeexclusive_items=False,
        show_isbuyboxwinner_items=False,
        show_freeshipping_items=False,
        show_discount_items=False,
        discount_percentage=0,
    )

    assert await lg.filter_param_item(search, item, show_discount_items=False, discount_percentage=0) is True


async def test_filter_param_item_discount_threshold(links_module):
    LinksGenerator = links_module.LinksGenerator
    from affiliate_mktg.src.core.models import (
        Item, Offers, Listing, Availability, DeliveryInfo, ProgramEligibility, Price, Savings, SearchInput
    )

    lg = LinksGenerator()

    listing = Listing(
        condition=1,
        id="1",
        isBuyBoxWinner=True,
        availability=Availability(maxOrderQuantity="1", message="ok", minOrderQuantity="1", type="AVAILABLE"),
        deliveryInfo=DeliveryInfo(isAmazonFulfilled=True, isFreeShippingEligible=True, isPrimeEligible=True, shippingCharges="0"),
        programEligibility=ProgramEligibility(isAll=True, isPrimeExclusive=False, isPrimeEarlyAccess=False),
        price=Price(amount=10.0, currency="USD", display_amount=10.0,
                    savings=Savings(amount=2, currency="USD", display_amount=2, percentage=20)),
    )

    item = Item(
        asin="A",
        detail_page_url="u",
        short_display_value="s",
        display_value="d",
        offers=Offers(listings=[listing]),
        images=[],
    )

    search = SearchInput(
        keywords="k",
        search_index="idx",
        item_count=1,
        show_availability_type=[],
        show_prime_delivery_items=False,
        show_isprimeexclusive_items=False,
        show_isbuyboxwinner_items=False,
        show_freeshipping_items=False,
        show_discount_items=True,
        discount_percentage=15,
    )

    assert await lg.filter_param_item(search, item, show_discount_items=True, discount_percentage=15) is True
    assert await lg.filter_param_item(search, item, show_discount_items=True, discount_percentage=25) is False


async def test_generate_link_maps_item_and_filters_in(links_module, monkeypatch):
    LinksGenerator = links_module.LinksGenerator
    from affiliate_mktg.src.core.models import SearchInput
    from affiliate_mktg.src.core.enums import ImageType

    lg = LinksGenerator()

    # Patch get_default_api so we don't depend on configValues / real AmazonCreatorsApi
    class FakeApi:
        def search_items(self, **kwargs):
            fake_item = make_fake_sdk_item(
                asin="B000123",
                url="https://amazon.com/dp/B000123",
                title="My Product: Deluxe, Edition",
                availability_type="AVAILABLE",
                savings_percentage=20,
            )
            return SimpleNamespace(items=ItemsContainer([fake_item]))

    async def fake_get_default_api():
        return FakeApi(), "tag", "marketplace"

    monkeypatch.setattr(lg, "get_default_api", fake_get_default_api)

    search = SearchInput(
        keywords="headphones",
        search_index="Electronics",
        item_count=1,
        show_availability_type=[],               # no filtering
        show_prime_delivery_items=False,
        show_isprimeexclusive_items=False,
        show_isbuyboxwinner_items=False,
        show_freeshipping_items=False,
        show_discount_items=False,
        discount_percentage=0,
    )

    items = await lg.generate_link(search)

    assert isinstance(items, list)
    assert len(items) == 1

    item = items[0]
    assert item.asin == "B000123"
    assert item.detail_page_url == "https://amazon.com/dp/B000123"
    assert item.display_value == "My Product: Deluxe, Edition"

    # short_display_value = split(":")[0].split(",")[0]
    assert item.short_display_value == "My Product"

    # images mapped
    assert len(item.images) == 3
    assert {img.image_type for img in item.images} == {ImageType.LARGE, ImageType.MEDIUM, ImageType.SMALL}

    # offers/listings mapped
    assert item.offers.listings
    listing = item.offers.listings[0]
    assert listing.isBuyBoxWinner is True
    assert listing.availability.type == "AVAILABLE"
    assert listing.price.amount == 99.99
    assert listing.price.currency == "USD"
    assert listing.price.savings.percentage == 20


async def test_generate_link_no_results_returns_empty(links_module, monkeypatch):
    LinksGenerator = links_module.LinksGenerator
    from affiliate_mktg.src.core.models import SearchInput

    lg = LinksGenerator()

    class FakeApi:
        def search_items(self, **kwargs):
            return SimpleNamespace(items=ItemsContainer([]))

    async def fake_get_default_api():
        return FakeApi(), "tag", "marketplace"

    monkeypatch.setattr(lg, "get_default_api", fake_get_default_api)

    search = SearchInput(
        keywords="anything",
        search_index="All",
        item_count=1,
        show_availability_type=[],
        show_prime_delivery_items=False,
        show_isprimeexclusive_items=False,
        show_isbuyboxwinner_items=False,
        show_freeshipping_items=False,
        show_discount_items=False,
        discount_percentage=0,
    )

    items = await lg.generate_link(search)
    assert items == []


async def test_generate_link_api_exception_does_not_raise(links_module, monkeypatch):
    LinksGenerator = links_module.LinksGenerator
    ApiException = importlib.import_module("creatorsapi_python_sdk.rest").ApiException
    from affiliate_mktg.src.core.models import SearchInput

    lg = LinksGenerator()

    class FakeApi:
        def search_items(self, **kwargs):
            raise ApiException(status=503, body="down", headers={"x-amzn-RequestId": "X"})

    async def fake_get_default_api():
        return FakeApi(), "tag", "marketplace"

    monkeypatch.setattr(lg, "get_default_api", fake_get_default_api)

    search = SearchInput(
        keywords="anything",
        search_index="All",
        item_count=1,
        show_availability_type=[],
        show_prime_delivery_items=False,
        show_isprimeexclusive_items=False,
        show_isbuyboxwinner_items=False,
        show_freeshipping_items=False,
        show_discount_items=False,
        discount_percentage=0,
    )

    # Should swallow the exception and return None (implicit) or [] depending on your code path
    result = await lg.generate_link(search)
    assert result is None or result == []

async def test_save_and_load_response_json_roundtrip(links_module, tmp_path, monkeypatch):
    LinksGenerator = links_module.LinksGenerator
    lg = LinksGenerator()

    monkeypatch.chdir(tmp_path)

    class FakeResponse:
        def to_dict(self):
            return {"ok": True, "items": [1, 2, 3]}

    await lg.save_response_json(FakeResponse())
    assert (tmp_path / "paapi_response.json").exists()

    data = await lg.get_response_json()
    assert data == {"ok": True, "items": [1, 2, 3]}