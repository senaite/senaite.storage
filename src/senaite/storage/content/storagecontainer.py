# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from Products.Archetypes.atapi import registerType
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.idserver import renameAfterCreation
from plone.app.folder.folder import ATFolder
from senaite.storage import PRODUCT_NAME
from senaite.storage.interfaces import IStorageContainer
from zope.interface import implements

schema = BikaFolderSchema.copy()

class StorageContainer(ATFolder):
    """Container for the storage of other storage containers
    """
    implements(IStorageContainer)
    _at_rename_after_creation = True
    displayContentsTab = False
    schema = schema

    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)


registerType(StorageContainer, PRODUCT_NAME)
