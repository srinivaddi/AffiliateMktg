import json
import creatorsapi_python_sdk
from creatorsapi_python_sdk.models.search_items_request_content import SearchItemsRequestContent
from creatorsapi_python_sdk.models.search_items_resource import SearchItemsResource
from creatorsapi_python_sdk.rest import ApiException
from amazon_creatorsapi import AmazonCreatorsApi, Country
from affiliate_mktg.src.config.amazon_loader import get_amazon_config
from affiliate_mktg.src.core.models import (
    Item,
    Offers,
    Listing,
    Price,
    Savings,
    Image,
    SearchInput,
    Availability,
    DeliveryInfo,
    ProgramEligibility,
)
from affiliate_mktg.src.core.enums import ImageType
# from affiliate_mktg.core.model_response import PAAPIResponse
from affiliate_mktg.src.utils.logging_setup import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)
configValues = get_amazon_config()

class LinksGenerator:
    def __init__(self):
        logger.info("Starting affiliate marketing link generator...")

    async def get_default_api(self):
        access_key_creatorsapi = configValues["CREDENTIAL_ID_CREATORSAPI"]
        secret_key_creatorsapi = configValues["CREDENTIAL_SECRET_CREATORSAPI"]
        version_creatorsapi = configValues["VERSION_CREATORSAPI"]
        partner_tag = configValues["PARTNER_TAG"]
        encryption_key = configValues["ENCRYPTION_KEY"]
        marketplace = configValues["MARKETPLACE"]
        throttle_delay = configValues["THROTTLE_DELAY"]
        host = configValues["HOST"]
        region = configValues["REGION"]

        default_api = AmazonCreatorsApi(
            credential_id=access_key_creatorsapi,
            credential_secret=secret_key_creatorsapi,
            version=version_creatorsapi,
            tag=partner_tag,
            country=Country.US,
            marketplace=marketplace,
            throttling = 1,
        )

        return default_api, partner_tag, marketplace

    async def generate_link(self, searchInput: SearchInput):
        self.default_api, self.partner_tag, marketplace = await self.get_default_api()

        search_items_resources = [
                SearchItemsResource.IMAGES_DOT_PRIMARY_DOT_LARGE,
                SearchItemsResource.ITEM_INFO_DOT_TITLE,
                SearchItemsResource.ITEM_INFO_DOT_TITLE,
                SearchItemsResource.OFFERS_V2_DOT_LISTINGS_DOT_AVAILABILITY,
                SearchItemsResource.OFFERS_V2_DOT_LISTINGS_DOT_CONDITION,
                SearchItemsResource.OFFERS_V2_DOT_LISTINGS_DOT_DEAL_DETAILS,
                SearchItemsResource.OFFERS_V2_DOT_LISTINGS_DOT_IS_BUY_BOX_WINNER,
                SearchItemsResource.OFFERS_V2_DOT_LISTINGS_DOT_LOYALTY_POINTS,
                SearchItemsResource.OFFERS_V2_DOT_LISTINGS_DOT_MERCHANT_INFO,
                SearchItemsResource.OFFERS_V2_DOT_LISTINGS_DOT_MERCHANT_INFO,
                SearchItemsResource.OFFERS_V2_DOT_LISTINGS_DOT_PRICE,
                SearchItemsResource.OFFERS_V2_DOT_LISTINGS_DOT_TYPE
            ]

        try:
            response = self.default_api.search_items(
                keywords=searchInput.keywords,
                search_index=searchInput.search_index,
                item_count=searchInput.item_count,
                resources=search_items_resources
            )

            logger.info("API called Successfully")
            logger.info("Complete Response:", response)

            items_all = []

            if response.items.count == 0:
                logger.info(
                    "The call to SearchItems returned no results"
                )
            else:
                logger.info("Printing first item information in SearchResult:")
                for itm in response.items:
                    logger.info(itm.asin)
                    item = Item(
                        asin="",
                        detail_page_url="",
                        short_display_value="",
                        display_value="",
                        offers=Offers(listings=[]),
                        images=[],
                    )
                    if itm is not None:
                        if itm.asin is not None:
                            logger.info("ASIN: ", itm.asin)
                            item.asin = itm.asin
                        if itm.detail_page_url is not None:
                            logger.info("DetailPageURL: ", itm.detail_page_url)
                            item.detail_page_url = itm.detail_page_url
                        if (
                            itm.images is not None
                            and itm.images.primary is not None
                        ):
                            images = []
                            if itm.images.primary.large is not None:
                                image = Image(
                                    image_type=ImageType.LARGE,
                                    height=itm.images.primary.large.height,
                                    width=itm.images.primary.large.width,
                                    url=itm.images.primary.large.url,
                                )
                                images.append(image)
                            if itm.images.primary.medium is not None:
                                image = Image(
                                    image_type=ImageType.MEDIUM,
                                    height=itm.images.primary.medium.height,
                                    width=itm.images.primary.medium.width,
                                    url=itm.images.primary.medium.url,
                                )
                                images.append(image)
                            if itm.images.primary.small is not None:
                                image = Image(
                                    image_type=ImageType.SMALL,
                                    height=itm.images.primary.small.height,
                                    width=itm.images.primary.small.width,
                                    url=itm.images.primary.small.url,
                                )
                                images.append(image)
                            item.images = images
                        if (
                            itm.item_info is not None
                            and itm.item_info.title is not None
                            and itm.item_info.title.display_value is not None
                        ):
                            logger.info(
                                "Title: ", itm.item_info.title.display_value
                            )
                            item.display_value = itm.item_info.title.display_value
                            short_display_value = (
                                itm.item_info.title.display_value.split(":")[0]
                                .split(",")[0]
                            )
                            logger.info(
                                f"Short name by delimiter: {short_display_value}"
                            )
                            item.short_display_value = short_display_value
                        if (
                            itm.offers_v2 is not None
                            and itm.offers_v2.listings is not None
                        ):
                            listings = []
                            for lstng in itm.offers_v2.listings:
                                availability = Availability(
                                    maxOrderQuantity=None,
                                    message=None,
                                    minOrderQuantity=None,
                                    type=None,
                                )
                                savings = Savings(
                                    amount=0.0,
                                    currency="",
                                    display_amount=0.0,
                                    percentage=0.0,
                                )
                                price = Price(
                                    amount=0.0,
                                    currency="",
                                    display_amount=0.0,
                                    savings=savings,
                                )
                                deliveryInfo = DeliveryInfo(
                                    isAmazonFulfilled=False,
                                    isFreeShippingEligible=False,
                                    isPrimeEligible=False,
                                    shippingCharges=None,
                                )
                                programEligibility = ProgramEligibility(
                                    isAll=False,
                                    isPrimeExclusive=False,
                                    isPrimeEarlyAccess=False,
                                )
                                listing = Listing(
                                    condition="",
                                    id="",
                                    isBuyBoxWinner=False,
                                    availability=availability,
                                    price=price,
                                    deliveryInfo=deliveryInfo,
                                    programEligibility=programEligibility,
                                )

                                listing.condition = (
                                    lstng.condition
                                    if lstng.condition is not None
                                    else "N/A"
                                )
                                listing.isBuyBoxWinner = (
                                    lstng.is_buy_box_winner
                                    if lstng.is_buy_box_winner is not None
                                    else False
                                )
                                if (
                                    listing.price is not None
                                    and lstng.price is not None
                                    and lstng.price.money is not None
                                ):
                                    listing.price.amount = (
                                        lstng.price.money.amount
                                        if lstng.price.money.amount is not None
                                        else 0.0
                                    )
                                    listing.price.display_amount = (
                                        lstng.price.money.display_amount
                                        if lstng.price.money.display_amount is not None
                                        else ""
                                    )
                                    listing.price.currency = (
                                        lstng.price.money.currency
                                        if lstng.price.money.currency is not None
                                        else ""
                                    )
                                if (
                                    listing.price is not None
                                    and lstng.price is not None
                                    and lstng.price.savings is not None
                                ):
                                    listing.price.savings.amount = (
                                        lstng.price.savings.money.amount
                                        if lstng.price.savings.money.amount  is not None
                                        else 0.0
                                    )
                                    listing.price.savings.display_amount = (
                                        lstng.price.savings.money.display_amount
                                        if lstng.price.savings.money.display_amount  is not None
                                        else ""
                                    )
                                    listing.price.savings.currency = (
                                        lstng.price.savings.money.currency
                                        if lstng.price.savings.money.currency  is not None
                                        else ""
                                    )
                                    listing.price.savings.percentage = (
                                        lstng.price.savings.percentage
                                        if lstng.price.savings.percentage is not None
                                        else 0
                                    )

                                if lstng.availability is not None:
                                    availability.maxOrderQuantity = (
                                        lstng.availability.max_order_quantity
                                        if lstng.availability.max_order_quantity is not None
                                        else None
                                    )
                                    availability.message = (
                                        lstng.availability.message
                                        if lstng.availability.message is not None
                                        else None
                                    )
                                    availability.minOrderQuantity = (
                                        lstng.availability.min_order_quantity
                                        if lstng.availability.min_order_quantity is not None
                                        else None
                                    )
                                    availability.type = (
                                        lstng.availability.type
                                        if lstng.availability.type is not None
                                        else None
                                    )
                                    listing.availability = availability
                                if lstng.deal_details is not None:
                                    programEligibility.isAll = (
                                        lstng.deal_details is not None and lstng.deal_details.access_type is not None and lstng.deal_details.access_type == "ALL" 
                                    )
                                    programEligibility.isPrimeExclusive = (
                                        lstng.deal_details is not None and lstng.deal_details.access_type is not None and lstng.deal_details.access_type == "PRIME_EXCLUSIVE" 
                                    )
                                    programEligibility.isPrimeEarlyAccess = (
                                        lstng.deal_details is not None and lstng.deal_details.access_type is not None and lstng.deal_details.access_type == "PRIME_EARLY_ACCESS" 
                                    )
                                    listing.programEligibility = (
                                        programEligibility
                                    )

                                listings.append(listing)
                            item.offers = Offers(listings=listings)

                        if await self.filter_param_item(
                            searchInput, item, searchInput.show_discount_items, searchInput.discount_percentage
                        ):
                            items_all.append(item)
            # else:
            #     logger.info(
            #         "The call to SearchItems returned no results"
            #     )

            return items_all

        except ApiException as exception:
            logger.error(
                "Error calling Creators API 6.0!", exc_info=True
            )
            logger.error("Status code:", exception.status, exc_info=True)
            logger.error("Errors :", exception.body, exc_info=True)
            logger.error(
                "Request ID:",
                exception.headers["x-amzn-RequestId"],
                exc_info=True,
            )
        except TypeError as exception:
            logger.error("TypeError :", exception, exc_info=True)
        except ValueError as exception:
            logger.error("ValueError :", exception, exc_info=True)
        except Exception as exception:
            logger.error("Exception :", exception, exc_info=True)

    async def filter_param_item(
        self, searchInput: SearchInput, item: Item, show_discount_items: bool, discount_percentage: int
    ):
        if item.offers.listings:
            for lstng in item.offers.listings:
                is_valid = True

                if searchInput.show_availability_type:
                    desired = searchInput.show_availability_type

                    if isinstance(desired, (list, tuple, set)):
                        desired_values = [getattr(d, "value", d) for d in desired if d is not None and str(d) != ""]
                    else:
                        desired_values = [getattr(desired, "value", desired)]

                    # only enforce filter when the provided list has one or more values
                    if desired_values:
                        if not (
                            lstng.availability
                            and lstng.availability.type
                            and any(
                                str(lstng.availability.type).upper() == str(val).upper()
                                for val in desired_values
                            )
                        ):
                            is_valid = False

                if searchInput.show_isbuyboxwinner_items:
                    if not (
                        lstng.isBuyBoxWinner
                        and lstng.isBuyBoxWinner
                        == searchInput.show_isbuyboxwinner_items
                    ):
                        is_valid = False

                if searchInput.show_prime_delivery_items:
                    if not (
                        lstng.deliveryInfo
                        and lstng.deliveryInfo.isPrimeEligible
                        and lstng.deliveryInfo.isPrimeEligible
                        == searchInput.show_prime_delivery_items
                    ):
                        is_valid = False

                if searchInput.show_isprimeexclusive_items:
                    if not (
                        lstng.programEligibility
                        and lstng.programEligibility.isPrimeExclusive
                        and lstng.programEligibility.isPrimeExclusive
                        == searchInput.show_isprimeexclusive_items
                    ):
                        is_valid = False

                if searchInput.show_freeshipping_items:
                    if not (
                        lstng.deliveryInfo
                        and lstng.deliveryInfo.isFreeShippingEligible
                        and lstng.deliveryInfo.isFreeShippingEligible
                        == searchInput.show_freeshipping_items
                    ):
                        is_valid = False

                if discount_percentage:
                    if not (
                        lstng.price.savings.percentage
                        and lstng.price.savings.percentage >= discount_percentage
                    ):
                        is_valid = False

                if is_valid:
                    return True
        else:
            if not show_discount_items and discount_percentage == 0:
                return True

        return False

    async def save_response_json(self, response):
        response_dict = response.to_dict()
        filename = "paapi_response.json"
        with open(filename, "w", encoding="utf-8") as outfile:
            json.dump(response_dict, outfile, indent=4)

    async def get_response_json(self):
        with open("paapi_response.json", "r", encoding="utf-8") as infile:
            data = json.load(infile)
        return data
