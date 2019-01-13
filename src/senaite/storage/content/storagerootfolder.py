# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from Products.Archetypes.atapi import registerType
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IHaveNoBreadCrumbs
from plone.app.folder.folder import ATFolder
from senaite.storage import PRODUCT_NAME
from senaite.storage.interfaces import IStorageRootFolder
from zope.interface import implements

schema = BikaFolderSchema.copy()

class StorageRootFolder(ATFolder):
    """Storage module root object
    """
    implements(IStorageRootFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema

registerType(StorageRootFolder, PRODUCT_NAME)
