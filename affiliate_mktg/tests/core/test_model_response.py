import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from affiliate_mktg.src.core.model_response import (
    Savings,
    Price,
    Listing,
    Offers,
    Title,
    ItemInfo,
    ImageSize,
    PrimaryImage,
    Images,
    Item,
    SearchResult,
    PAAPIResponse,
)

def test_savings_creation():
    savings = Savings(
        amount=10.0,
        currency="USD",
        display_amount="$10",
        percentage=20,
        price_per_unit=None,
    )

    assert savings.amount == 10.0
    assert savings.currency == "USD"
    assert savings.display_amount == "$10"
    assert savings.percentage == 20
    assert savings.price_per_unit is None

def test_price_with_savings():
    savings = Savings(
        amount=5.0,
        currency="USD",
        display_amount="$5",
        percentage=10,
        price_per_unit=None,
    )

    price = Price(
        amount=45.0,
        currency="USD",
        display_amount="$45",
        price_per_unit=None,
        savings=savings,
    )

    assert price.amount == 45.0
    assert price.savings is savings

def test_listing_and_offers_creation():
    price = Price(
        amount=100.0,
        currency="USD",
        display_amount="$100",
        price_per_unit=None,
        savings=None,
    )

    listing = Listing(
        availability="IN_STOCK",
        condition="NEW",
        delivery_info=None,
        id="listing123",
        is_buy_box_winner=True,
        loyalty_points=None,
        merchant_info=None,
        price=price,
        program_eligibility=None,
        promotions=None,
        saving_basis=None,
        violates_map=False,
    )

    offers = Offers(
        listings=[listing],
        summaries=None,
    )

    assert offers.listings[0].id == "listing123"
    assert offers.listings[0].price.amount == 100.0

def test_item_info_and_images():
    title = Title(
        display_value="Test Product",
        label="Title",
        locale="en_US",
    )

    item_info = ItemInfo(
        title=title,
        by_line_info=None,
        classifications=None,
        content_info=None,
        content_rating=None,
        external_ids=None,
        features=None,
        manufacture_info=None,
        product_info=None,
        technical_info=None,
        trade_in_info=None,
    )

    large_image = ImageSize(
        url="http://example.com/large.jpg",
        height=500,
        width=500,
    )

    images = Images(
        primary=PrimaryImage(
            small=None,
            medium=None,
            large=large_image,
        ),
        variants=None,
    )

    assert item_info.title.display_value == "Test Product"
    assert images.primary.large.url.endswith(".jpg")

def test_item_creation():
    price = Price(
        amount=20.0,
        currency="USD",
        display_amount="$20",
        price_per_unit=None,
        savings=None,
    )

    listing = Listing(
        availability="IN_STOCK",
        condition=None,
        delivery_info=None,
        id="id1",
        is_buy_box_winner=None,
        loyalty_points=None,
        merchant_info=None,
        price=price,
        program_eligibility=None,
        promotions=None,
        saving_basis=None,
        violates_map=False,
    )

    offers = Offers(listings=[listing], summaries=None)

    item = Item(
        asin="B000123",
        browse_node_info=None,
        detail_page_url="http://example.com",
        images=Images(
            primary=PrimaryImage(
                small=None,
                medium=None,
                large=ImageSize(
                    url="http://example.com/img.jpg",
                    height=200,
                    width=200,
                ),
            ),
            variants=None,
        ),
        item_info=ItemInfo(
            title=Title("Name", "Label", "en_US"),
            by_line_info=None,
            classifications=None,
            content_info=None,
            content_rating=None,
            external_ids=None,
            features=None,
            manufacture_info=None,
            product_info=None,
            technical_info=None,
            trade_in_info=None,
        ),
        offers=offers,
        parent_asin=None,
        rental_offers=None,
        score=None,
        variation_attributes=None,
    )

    assert item.asin == "B000123"
    assert item.offers.listings[0].price.amount == 20.0

def test_search_result_creation():
    search_result = SearchResult(
        total_result_count=1,
        search_url="http://search.example.com",
        items=[],
        search_refinements=None,
    )

    assert search_result.total_result_count == 1
    assert search_result.items == []

def test_paapi_response_dynamic_init():
    response = PAAPIResponse(
        search_result="result",
        errors=None,
        extra_field="extra",
    )

    assert response.search_result == "result"
    assert response.errors is None
    assert response.extra_field == "extra"
    