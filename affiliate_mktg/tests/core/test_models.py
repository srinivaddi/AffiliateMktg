import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from affiliate_mktg.src.core.enums import ImageType, AvailabilityType
from affiliate_mktg.src.core.models import (
    Image,
    Savings,
    Price,
    Availability,
    DeliveryInfo,
    ProgramEligibility,
    Listing,
    Offers,
    Item,
    BlogInputConfig,
    SearchIndex,
    SearchInput,
)

def test_image_creation():
    image = Image(
        image_type=ImageType.LARGE,
        height=500,
        width=500,
        url="https://example.com/image.jpg",
    )

    assert image.image_type == ImageType.LARGE
    assert image.height == 500
    assert image.width == 500
    assert image.url.endswith(".jpg")


def test_savings_creation():
    savings = Savings(
        amount=10.0,
        currency="USD",
        display_amount=10.0,
        percentage=20.0,
    )

    assert savings.amount == 10.0
    assert savings.currency == "USD"
    assert savings.percentage == 20.0


def test_price_with_savings():
    savings = Savings(
        amount=5.0,
        currency="USD",
        display_amount=5.0,
        percentage=10.0,
    )

    price = Price(
        amount=45.0,
        currency="USD",
        display_amount=45.0,
        savings=savings,
    )

    assert price.amount == 45.0
    assert price.savings.amount == 5.0

def test_listing_creation():
    listing = Listing(
        condition=1,
        id="listing-1",
        isBuyBoxWinner=True,
        availability=Availability(
            maxOrderQuantity="10",
            minOrderQuantity="1",
            message="In stock",
            type="AVAILABLE",
        ),
        deliveryInfo=DeliveryInfo(
            isAmazonFulfilled=True,
            isFreeShippingEligible=True,
            isPrimeEligible=True,
            shippingCharges="0.00",
        ),
        programEligibility=ProgramEligibility(
            isAll=True,
            isPrimeExclusive=False,
            isPrimeEarlyAccess=False,
        ),
        price=Price(
            amount=99.99,
            currency="USD",
            display_amount=99.99,
            savings=Savings(
                amount=20.0,
                currency="USD",
                display_amount=20.0,
                percentage=20.0,
            ),
        ),
    )

    assert listing.isBuyBoxWinner is True
    assert listing.price.savings.percentage == 20.0
    assert listing.availability.message == "In stock"


def test_item_with_offers_and_images():
    item = Item(
        asin="B000123",
        detail_page_url="https://amazon.com/dp/B000123",
        short_display_value="Short title",
        display_value="Full display title",
        offers=Offers(
            listings=[]
        ),
        images=[
            Image(
                image_type=ImageType.LARGE,
                height=1000,
                width=1000,
                url="https://example.com/img.png",
            )
        ],
    )

    assert item.asin == "B000123"
    assert len(item.images) == 1
    assert item.images[0].image_type == ImageType.LARGE

def test_blog_input_config_creation():
    item = Item(
        asin="B1",
        detail_page_url="url",
        short_display_value="short",
        display_value="display",
        offers=Offers(listings=[]),
        images=[],
    )

    config = BlogInputConfig(
        items_arg=item,
        topic_arg="Topic",
        topic_arg_post="Post Topic",
        topicurl_arg="https://topic.url",
        labels_arg="label1,label2",
        systempromptrole_arg="role",
        systempromptstyle_arg="style",
    )

    assert config.items_arg.asin == "B1"
    assert "label1" in config.labels_arg

def test_search_index_optional_keywords():
    index = SearchIndex(
        search_index="Books",
        display_name="Books",
    )

    assert index.keywords is None


def test_search_index_with_keywords():
    index = SearchIndex(
        search_index="Electronics",
        display_name="Electronics",
        keywords=["laptop", "monitor"],
    )

    assert "laptop" in index.keywords

def test_search_input_creation():
    search = SearchInput(
        keywords="headphones",
        search_index="Electronics",
        item_count=10,
        show_availability_type=[AvailabilityType.INSTOCK],
        show_prime_delivery_items=True,
        show_isprimeexclusive_items=False,
        show_isbuyboxwinner_items=True,
        show_freeshipping_items=True,
        show_discount_items=True,
        discount_percentage=15,
    )

    assert search.item_count == 10
    assert AvailabilityType.INSTOCK in search.show_availability_type


def test_kw_only_enforced():
    with pytest.raises(TypeError):
        Image(
            ImageType.LARGE,
            100,
            100,
            "https://example.com/img.jpg",
        )