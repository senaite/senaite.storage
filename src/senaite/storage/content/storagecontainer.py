# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import registerType
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from senaite.storage import PRODUCT_NAME
from senaite.storage.interfaces import IStorageContainer
from zope.interface import implements

schema = ATFolderSchema.copy()

class StorageContainer(ATFolder):
    """Container for the storage of other storage containers
    """
    implements(IStorageContainer)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
registerType(StorageContainer, PRODUCT_NAME)
