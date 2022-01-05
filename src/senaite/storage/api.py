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
# Copyright 2019-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from senaite.storage import logger
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.config import STORAGE_WORKFLOW_ID


def remove_sample_from_container(sample):
    """Remove the sample from the container
    """
    # remove from container
    container = get_storage_sample(sample)
    if container:
        container.remove_object(sample)
    else:
        logger.warn("Container for Sample {} not found".format(
            api.get_id(sample)))


def get_storage_sample(sample, as_brain=False):
    """Returns the storage container of the sample
    """
    query = dict(portal_type="StorageSamplesContainer",
                 get_samples_uids=[api.get_uid(sample)])
    brains = api.search(query, STORAGE_CATALOG)
    if not brains:
        return None
    if as_brain:
        return brains[0]
    return api.get_object(brains[0])


def get_storage_catalog():
    """Returns the storage catalog
    """
    return api.get_tool(STORAGE_CATALOG)


def get_storage_workflow():
    """Returns the storage workflow
    """
    wf_tool = api.get_tool("portal_workflow")
    return wf_tool.getWorkflowByd(STORAGE_WORKFLOW_ID)


def get_parents(obj, parents=None, predicate=None):
    """Return all parents of the object
    """
    if parents is None:
        parents = []
    if predicate is None:
        predicate = api.is_portal
    parent = api.get_parent(obj)
    parents.append(parent)
    if predicate(parent):
        return parents
    return get_parents(parent, parents=parents, predicate=predicate)
