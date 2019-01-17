# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from Products.Archetypes.Schema import Schema
from Products.Archetypes.atapi import registerType
from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest
from senaite.storage import PRODUCT_NAME
from senaite.storage.content.storagelayoutcontainer import \
    StorageLayoutContainer
from senaite.storage.content.storagelayoutcontainer import schema
from senaite.storage.interfaces import IStorageSamplesContainer
from zope.interface import implements
from bika.lims import workflow as wf

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
        """Adds an object to the specified position. If an object already exists
        at the given position, return False. Otherwise, return True
        """
        stored = super(StorageSamplesContainer, self).add_object_at(
            object_brain_uid, row, column)
        if not stored:
            return False

        # Transition the sample to "stored" state
        object = api.get_object(object_brain_uid)
        wf.doActionFor(object, "store")
        return stored

registerType(StorageSamplesContainer, PRODUCT_NAME)