# -*- coding: utf-8 -*-

from senaite.storage import is_installed
from senaite.storage import logger
from senaite.storage.setuphandlers import post_install


def afterUpgradeStepHandler(event):
    """Event handler that is executed after running an upgrade step of senaite.core
    """
    if not is_installed():
        return
    logger.info("Run senaite.storage.afterUpgradeStepHandler ...")
    setup = event.context
    post_install(setup)
    logger.info("Run senaite.storage.afterUpgradeStepHandler [DONE]")
