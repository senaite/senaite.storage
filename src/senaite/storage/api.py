# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from bika.lims import api
from senaite.storage.catalog import SENAITE_STORAGE_CATALOG


def get_storage_sample(sample_obj_brain_or_uid, as_brain=False):
    """Returns the storage container the sample passed in is stored in
    """
    query = dict(portal_type="StorageSamplesContainer",
                 get_samples_uids=[api.get_uid(sample_obj_brain_or_uid)])
    brains = api.search(query, SENAITE_STORAGE_CATALOG)
    if not brains:
        return None
    if as_brain:
        return brains[0]
    return api.get_object(brains[0])
