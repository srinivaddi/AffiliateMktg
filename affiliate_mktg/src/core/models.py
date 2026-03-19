from dataclasses import dataclass
from typing import Optional

from affiliate_mktg.src.core.enums import ImageType, AvailabilityType


@dataclass(kw_only=True)
class Image:
    image_type: ImageType
    height: int
    width: int
    url: str


@dataclass(kw_only=True)
class Savings:
    amount: float
    currency: str
    display_amount: float
    percentage: float


@dataclass(kw_only=True)
class Price:
    amount: float
    currency: str
    display_amount: float
    savings: Savings

@dataclass(kw_only=True)
class Availability:
    maxOrderQuantity: str
    message: str
    minOrderQuantity: str
    type: str


@dataclass(kw_only=True)
class DeliveryInfo:
    isAmazonFulfilled: bool
    isFreeShippingEligible: bool
    isPrimeEligible: bool
    shippingCharges: str


@dataclass(kw_only=True)
class ProgramEligibility:
    isAll: bool
    isPrimeExclusive: bool
    isPrimeEarlyAccess: bool

@dataclass(kw_only=True)
class Listing:
    condition: int
    id: str
    isBuyBoxWinner: bool
    availability: Availability
    deliveryInfo: DeliveryInfo
    programEligibility: ProgramEligibility
    price: Price


@dataclass(kw_only=True)
class Offers:
    listings: list[Listing]


@dataclass(kw_only=True)
class Item:
    asin: str
    detail_page_url: str
    short_display_value: str
    display_value: str
    offers: Offers
    images: list[Image]


@dataclass(kw_only=True)
class BlogInputConfig:
    items_arg: Item
    topic_arg: str
    topic_arg_post: str
    topicurl_arg: str
    labels_arg: str
    systempromptrole_arg: str
    systempromptstyle_arg: str


@dataclass(kw_only=True)
class SearchIndex:
    search_index: str
    display_name: str
    keywords: Optional[list[str]] = None


@dataclass(kw_only=True)
class SearchInput:
    keywords: str
    search_index: str
    item_count: int
    show_availability_type: list[AvailabilityType]
    show_prime_delivery_items: bool
    show_isprimeexclusive_items: bool
    show_isbuyboxwinner_items: bool
    show_freeshipping_items: bool
    show_discount_items: bool
    discount_percentage: int
