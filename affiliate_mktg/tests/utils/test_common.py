import math
import time

import pytest

from affiliate_mktg.src.utils.common import (
    get_current_year_month,
    to_camel_case,
    get_elasped_time,
    is_similar_string,
    validate_arguments,
)


# -------------------------
# get_current_year_month
# -------------------------

def test_get_current_year_month_returns_valid_tuple():
    year, month = get_current_year_month()

    assert isinstance(year, int)
    assert isinstance(month, int)
    assert year >= 2000
    assert 1 <= month <= 12


# -------------------------
# to_camel_case
# -------------------------

@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("hello world", "Hello World"),
        ("multiple   spaces", "Multiple Spaces"),
        ("Already Capitalized", "Already Capitalized"),
        ("mixed CASE input", "Mixed Case Input"),
        ("single", "Single"),
        ("", ""),
    ],
)
def test_to_camel_case(input_str, expected):
    assert to_camel_case(input_str) == expected


# -------------------------
# get_elasped_time
# -------------------------

def test_get_elapsed_time_positive():
    start = 10.5
    end = 15.75
    assert math.isclose(get_elasped_time(start, end), 5.25)


def test_get_elapsed_time_zero():
    assert get_elasped_time(5.0, 5.0) == 0.0


def test_get_elapsed_time_negative():
    assert get_elasped_time(10.0, 5.0) == -5.0


# -------------------------
# is_similar_string
# -------------------------

def test_is_similar_string_exact_match():
    assert is_similar_string("hello", "hello", threshold=1.0) is True


def test_is_similar_string_high_similarity():
    assert is_similar_string("affiliate", "affiliates", threshold=0.8) is True


def test_is_similar_string_below_threshold():
    assert is_similar_string("affiliate", "marketing", threshold=0.8) is False


def test_is_similar_string_empty_strings():
    assert is_similar_string("", "", threshold=1.0) is True


def test_is_similar_string_one_empty():
    assert is_similar_string("text", "", threshold=0.1) is False


# -------------------------
# validate_arguments
# -------------------------

def test_validate_arguments_generate_and_post_valid():
    valid, topic, topicurl, labels, role, style = validate_arguments(
        generate_blog=True,
        post_blog=True,
        topic="Affiliate Marketing",
        labels="Amazon",
        systempromptrole="Blogger",
        systempromptstyle="Professional",
    )

    assert valid is True
    assert topic == "Affiliate Marketing"
    assert topicurl == "affiliate-marketing"
    assert labels == "Amazon"
    assert role == "Blogger"
    assert style == "Professional"


def test_validate_arguments_generate_only_valid():
    valid, topic, topicurl, role, style = validate_arguments(
        generate_blog=True,
        post_blog=False,
        topic="SEO Tips",
        labels="",
        systempromptrole="Writer",
        systempromptstyle="Casual",
    )

    assert valid is True
    assert topicurl == "seo-tips"


def test_validate_arguments_post_only_valid():
    valid, topic, topicurl, labels = validate_arguments(
        generate_blog=False,
        post_blog=True,
        topic="Tech Gadgets",
        labels="Electronics",
        systempromptrole="",
        systempromptstyle="",
    )

    assert valid is True
    assert topicurl == "tech-gadgets"
    assert labels == "Electronics"


def test_validate_arguments_missing_topic_invalid():
    valid, *_ = validate_arguments(
        generate_blog=True,
        post_blog=True,
        topic="",
        labels="Amazon",
        systempromptrole="Role",
        systempromptstyle="Style",
    )

    assert valid is False


def test_validate_arguments_missing_labels_when_required_invalid():
    valid, *_ = validate_arguments(
        generate_blog=True,
        post_blog=True,
        topic="Affiliate Marketing",
        labels="",
        systempromptrole="Role",
        systempromptstyle="Style",
    )

    assert valid is False