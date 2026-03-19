import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from affiliate_mktg.src.core.enums import Models, ImageType, AvailabilityType

def test_models_enum_values():
    assert Models.LLAMA.value == "llama3.1"


def test_image_type_enum_values():
    assert ImageType.LARGE.value == "large"
    assert ImageType.MEDIUM.value == "medium"
    assert ImageType.SMALL.value == "small"


def test_availability_type_enum_values():
    assert AvailabilityType.INSTOCK.value == "IN_STOCK"
    assert AvailabilityType.INSTOCKSCARCE.value == "IN_STOCK_SCARCE"
    assert AvailabilityType.UNKNOWN.value == "UNKNOWN"

def test_models_enum_default():
    assert Models.default() == "llama3.1"


def test_image_type_enum_default():
    assert ImageType.default() == "large"


def test_availability_type_enum_default():
    assert AvailabilityType.default() == "IN_STOCK"
    
def test_enum_lookup_by_value():
    assert Models("llama3.1") is Models.LLAMA
    assert ImageType("medium") is ImageType.MEDIUM
    assert AvailabilityType("UNKNOWN") is AvailabilityType.UNKNOWN