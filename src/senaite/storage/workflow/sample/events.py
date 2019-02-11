# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from bika.lims import api
from senaite.storage import api as _api
from senaite.storage import logger


def after_recover(sample):
    """Unassigns the sample from its storage container and "recover"
    """
    container = _api.get_storage_sample(api.get_uid(sample))
    if not container:
        logger.warn("Container for Sample {} not found".format(sample.getId()))
        return False
    return container.remove_object(sample)
