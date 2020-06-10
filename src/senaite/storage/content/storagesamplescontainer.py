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

from Products.Archetypes.Schema import Schema
from Products.Archetypes.atapi import registerType
from bika.lims import api
from bika.lims import workflow as wf
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.interfaces import IAnalysisRequest
from senaite.storage import PRODUCT_NAME
from senaite.storage.content.storagelayoutcontainer import \
    StorageLayoutContainer
from senaite.storage.content.storagelayoutcontainer import schema
from senaite.storage.interfaces import IStorageSamplesContainer
from zope.interface import implements

schema = schema.copy() + Schema((
))


class StorageSamplesContainer(StorageLayoutContainer):
    """Container for the storage of samples
    """
    implements(IStorageSamplesContainer)
    schema = schema
    default_samples_capacity = 1

    def is_object_allowed(self, object_brain_uid):
        """Returns whether the type of object can be stored or not in this
        container. This function returns true if the object is allowed, even
        if the container already contains the object
        """
        # TODO Filer by sample type, volume, etc.
        # Only objects from IAnalysisRequest are allowed
        obj = api.get_object(object_brain_uid)
        return IAnalysisRequest.providedBy(obj)

    def add_object_at(self, object_brain_uid, row, column):
        """Adds an sample to the specified position. If an object already exists
        at the given position, return False.
        """
        if not self.can_add_object(object_brain_uid, row, column):
            return False

        sample = api.get_object(object_brain_uid)
        stored = super(StorageSamplesContainer, self).add_object_at(sample,
                                                                    row, column)
        if not stored:
            return False

        # Transition the sample to "stored" state
        # TODO check if the sample has a container assigned in BeforeTransition
        # If it does not have a container assigned, change the workflow state
        # to the previous one automatically (integrity-check)
        self.reindexObject(idxs=["get_samples_uids", "is_full"])
        sample = api.get_object(sample)
        wf.doActionFor(sample, "store")
        return stored

    def remove_object(self, object_brain_uid, notify_parent=True):
        """Removes the object from the container, if in there
        """
        removed = super(StorageSamplesContainer, self).remove_object(
            object_brain_uid, notify_parent=notify_parent)
        if not removed:
            return False

        # Do "recover" transition to sample
        # TODO Better to do this remove_object call from WF's AfterTransition
        # Otherwise, transition can be triggered through DC Workflow without
        # the container being notified.
        self.reindexObject(idxs=["get_samples_uids", "is_full"])
        sample = api.get_object(object_brain_uid)
        wf.doActionFor(sample, "recover")
        return removed

    def has_samples(self):
        """Returns whether this sample container contains samples or not
        """
        return len(self.get_samples_uids()) > 0

    def get_samples_uids(self):
        """Returns the uids of the samples this container contains
        """
        uids = map(lambda item: item.get("uid", ""), self.getPositionsLayout())
        return filter(api.is_uid, uids)

    def get_samples(self, as_brains=False):
        samples_uids = self.get_samples_uids()
        if not samples_uids:
            return []
        query = dict(portal_type="AnalysisRequest", UID=samples_uids)
        brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
        if as_brains:
            return brains
        return map(api.get_object, brains)

    # TODO Finish this (index and searches are still missing)
    def get_sample_types_uids(self):
        """Returns the uids of the samples types of the samples this container
        contains, if any. This is mostly used for suggest searches with
        ZCTextIndex, that gives a higher score when the term is found more than
        once. Hence the list may contain duplicates
        """
        samples_uids = self.get_samples_uids()
        if not samples_uids:
            return []
        query = dict(UID=samples_uids)
        brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
        return map(lambda brain: brain.getSampleTypeUID, brains)


registerType(StorageSamplesContainer, PRODUCT_NAME)
