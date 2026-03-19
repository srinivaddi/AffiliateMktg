from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Savings:
    amount: float
    currency: str
    display_amount: str
    percentage: int
    price_per_unit: Optional[str]


@dataclass
class Price:
    amount: float
    currency: str
    display_amount: str
    price_per_unit: Optional[str]
    savings: Optional[Savings]


@dataclass
class Listing:
    availability: Optional[str]
    condition: Optional[str]
    delivery_info: Optional[str]
    id: str
    is_buy_box_winner: Optional[bool]
    loyalty_points: Optional[str]
    merchant_info: Optional[str]
    price: Price
    program_eligibility: Optional[str]
    promotions: Optional[str]
    saving_basis: Optional[str]
    violates_map: bool


@dataclass
class Offers:
    listings: List[Listing]
    summaries: Optional[str]


@dataclass
class Title:
    display_value: str
    label: str
    locale: str


@dataclass
class ItemInfo:
    title: Title
    by_line_info: Optional[str]
    classifications: Optional[str]
    content_info: Optional[str]
    content_rating: Optional[str]
    external_ids: Optional[str]
    features: Optional[str]
    manufacture_info: Optional[str]
    product_info: Optional[str]
    technical_info: Optional[str]
    trade_in_info: Optional[str]


@dataclass
class ImageSize:
    url: str
    height: int
    width: int


@dataclass
class PrimaryImage:
    small: Optional[ImageSize]
    medium: Optional[ImageSize]
    large: ImageSize


@dataclass
class Images:
    primary: PrimaryImage
    variants: Optional[str]


@dataclass
class Item:
    asin: str
    browse_node_info: Optional[str]
    detail_page_url: str
    images: Images
    item_info: ItemInfo
    offers: Offers
    parent_asin: Optional[str]
    rental_offers: Optional[str]
    score: Optional[str]
    variation_attributes: Optional[str]


@dataclass
class SearchResult:
    total_result_count: int
    search_url: str
    items: List[Item]
    search_refinements: Optional[str]


@dataclass
class PAAPIResponse:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    search_result: SearchResult
    errors: Optional[str]
