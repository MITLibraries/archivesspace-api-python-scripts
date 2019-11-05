import logging
import pytest
import structlog


@pytest.fixture(autouse=True, scope='session')
def logger():
    logger = structlog.get_logger()
    logging.basicConfig(format="%(message)s",
                        handlers=[logging.StreamHandler()], level=logging.INFO)
    return logger
