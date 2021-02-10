# -*- coding: utf-8 -*-

from senaite.storage.setuphandlers import post_install


def afterUpgradeStepHandler(event):
    """Event handler that is executed after running an upgrade step of senaite.core
    """
    setup = event.context
    post_install(setup)
