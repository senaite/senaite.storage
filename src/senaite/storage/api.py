# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE.
#
# SENAITE.STORAGE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2019-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from senaite.storage import logger
from senaite.storage.catalog import SENAITE_STORAGE_CATALOG

from bika.lims import api


def get_storage_sample(sample_obj_brain_or_uid, as_brain=False):
    """Returns the storage container the sample passed in is stored in
    """
    catalog = get_storage_catalog()
    if not catalog:
        # Might be the product is not installed or catalog not present
        logger.warn("Senaite storage catalog not found")
        return None

    query = dict(portal_type="StorageSamplesContainer",
                 get_samples_uids=[api.get_uid(sample_obj_brain_or_uid)])
    brains = api.search(query, catalog.id)
    if not brains:
        return None
    if as_brain:
        return brains[0]
    return api.get_object(brains[0])


def get_storage_catalog():
    """Returns the storage catalog tool or None
    """
    return api.get_tool(SENAITE_STORAGE_CATALOG, default=None)
