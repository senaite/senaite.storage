# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from bika.lims import api
from senaite.storage import api as _api
from senaite.storage import logger


def AfterTransitionSampleEventHandler(sample, event):
    """Actions to be done after a transition for this sample takes place
    """
    if not event.transition:
        return

    if event.transition.id == "recover":
        handle_recover_sample(sample)


def handle_recover_sample(sample):
    """Unassigns the sample from its storage container and "recover"
    """
    container = _api.get_storage_sample(api.get_uid(sample))
    if not container:
        logger.warn("Container for Sample {} not found".format(sample.getId()))
        return False
    return container.remove_object(sample)
