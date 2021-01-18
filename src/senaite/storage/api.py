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

from bika.lims import api
from senaite.storage.catalog import SENAITE_STORAGE_CATALOG
from senaite.storage.config import STORAGE_CATALOG


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


def get_storage_catalog():
    """Returns the storage catalog

    Currently `portal_catalog`
    """
    return api.get_tool(STORAGE_CATALOG)


def get_storage_position_by_id(pid, include_inactive=False):
    """Get a storage position by ID

    :param pid: Unique storage position ID
    :param include_inactive: Include deactivated storage positions
    :returns: object or None
    """
    catalog = api.get_tool("portal_catalog")
    query = {
        "portal_type": "StoragePosition",
        "is_active": True,
    }
    # Remove active index
    if include_inactive:
        query.pop("is_active", None)
    results = catalog(query)
    count = len(results)
    if count == 0:
        return None

    # Create a position_id index
    for brain in results:
        obj = api.get_object(brain)
        if obj.position_id == pid:
            return obj

    return None
