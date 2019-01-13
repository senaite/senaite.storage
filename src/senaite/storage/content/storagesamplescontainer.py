# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.atapi import registerType
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.idserver import renameAfterCreation
from senaite.storage import PRODUCT_NAME
from senaite.storage.interfaces import IStorageSamplesContainer
from zope.interface import implements

schema = BikaSchema.copy()

class StorageSamplesContainer(BaseContent):
    """Container for the storage of samples
    """
    implements(IStorageSamplesContainer)
    _at_rename_after_creation = True
    displayContentsTab = False
    schema = schema

    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)

registerType(StorageSamplesContainer, PRODUCT_NAME)