import logging
import logging.config
from pathlib import Path
import time

import pytest

from affiliate_mktg.src.utils.logging_setup import (
    LOGGING_CONFIG,
    setup_logging,
    get_logger,
)

@pytest.fixture
def isolated_logging(monkeypatch, tmp_path):
    original_dict_config = logging.config.dictConfig

    config = LOGGING_CONFIG.copy()
    config["handlers"] = dict(LOGGING_CONFIG["handlers"])
    config["handlers"]["file"] = dict(LOGGING_CONFIG["handlers"]["file"])

    log_file = tmp_path / "test.log"
    config["handlers"]["file"]["filename"] = str(log_file)

    monkeypatch.setattr(
        logging.config,
        "dictConfig",
        lambda _: original_dict_config(config),
    )

    # Reset logging state
    logging.shutdown()
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    return log_file

def test_setup_logging_configures_root_logger(isolated_logging):
    setup_logging()

    root_logger = logging.getLogger()

    assert root_logger.level == logging.INFO
    assert len(root_logger.handlers) == 2

    handler_types = {type(h) for h in root_logger.handlers}
    assert logging.StreamHandler in handler_types
    assert logging.FileHandler in handler_types

# def test_setup_logging_writes_to_file(isolated_logging):
#     setup_logging()
#     logger = get_logger("test.logger")
#     logger.info("Hello logging")

#     log_file = isolated_logging
#     assert log_file.exists()

#     contents = log_file.read_text(encoding="utf-8")
#     assert "Hello logging" in contents
#     assert "test.logger" in contents
#     assert "INFO" in contents

def test_get_logger_returns_named_logger(isolated_logging):
    setup_logging()

    logger = get_logger("affiliate.test")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "affiliate.test"


def test_get_logger_inherits_root_handlers(isolated_logging):
    setup_logging()

    logger = get_logger("child.logger")

    assert logger.propagate is True or logger.handlers == []
    assert logging.getLogger().handlers  # root has handlers

def test_logging_config_has_expected_structure():
    assert LOGGING_CONFIG["version"] == 1
    assert "formatters" in LOGGING_CONFIG
    assert "handlers" in LOGGING_CONFIG
    assert "root" in LOGGING_CONFIG

    assert "console" in LOGGING_CONFIG["handlers"]
    assert "file" in LOGGING_CONFIG["handlers"]

    fmt = LOGGING_CONFIG["formatters"]["default"]["format"]
    assert "%(levelname)s" in fmt
    assert "%(name)s" in fmt