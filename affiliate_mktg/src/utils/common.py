from datetime import datetime
import difflib


def get_current_year_month():
    """
    Generates current year and month and returns them as a tuple.

    Returns:
        tuple: (year, month) from datetime.now().
    """
    now = datetime.now()
    return now.year, now.month


def to_camel_case(statement: str):
    """
    Converts a string to title case (capitalize each word).

    Parameters:
        statement (str): The input statement.

    Returns:
        str: The title-cased string.
    """
    words = statement.split()
    camel_cased = " ".join(word.capitalize() for word in words)
    return camel_cased


def get_elasped_time(start_time: float, end_time: float) -> float:
    """
    Calculates the time difference between two given times in seconds.

    Parameters:
        start_time (float): The start time in seconds.
        end_time (float): The end time in seconds.

    Returns:
        float: The time difference in seconds.
    """
    return end_time - start_time


def is_similar_string(str1: str, str2: str, threshold: float) -> bool:
    """
    Checks for similarity between two strings based on a threshold.

    Parameters:
        str1 (str): The first string.
        str2 (str): The second string.
        threshold (float): The comparison threshold.

    Returns:
        bool: True if similarity ratio >= threshold.
    """
    ratio = difflib.SequenceMatcher(None, str1, str2).ratio()
    return ratio >= threshold


def validate_arguments(
    generate_blog: bool,
    post_blog: bool,
    topic: str,
    labels: str,
    systempromptrole: str,
    systempromptstyle: str,
) -> tuple:
    valid = True
    topicurl = None
    if not topic:
        valid = False
    else:
        topicurl = to_camel_case(topic).lower().replace(" ", "-")
        if (generate_blog and post_blog) or (not generate_blog and post_blog):
            if not labels:
                valid = False

    if generate_blog and post_blog:
        return valid, topic, topicurl, labels, systempromptrole, systempromptstyle
    elif generate_blog and not post_blog:
        return valid, topic, topicurl, systempromptrole, systempromptstyle
    elif not generate_blog and post_blog:
        return valid, topic, topicurl, labels
