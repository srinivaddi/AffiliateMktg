from enum import Enum


class Models(Enum):
    LLAMA = "llama3.1"

    @classmethod
    def default(cls):
        return cls.LLAMA.value


class ImageType(Enum):
    LARGE = "large"
    MEDIUM = "medium"
    SMALL = "small"

    @classmethod
    def default(cls):
        return cls.LARGE.value


class AvailabilityType(Enum):
    INSTOCK = "IN_STOCK"
    INSTOCKSCARCE = "IN_STOCK_SCARCE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def default(cls):
        return cls.INSTOCK.value
