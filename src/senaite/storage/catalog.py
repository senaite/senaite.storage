# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from senaite.storage.interfaces import ISenaiteStorageCatalog
from zope.interface import implements

SENAITE_STORAGE_CATALOG = "senaite_storage_catalog"

class SenaiteStorageCatalog(BikaCatalogTool):
    implements(ISenaiteStorageCatalog)
    security = ClassSecurityInfo()

    def __init__(self):
        BikaCatalogTool.__init__(self,
                                 id=SENAITE_STORAGE_CATALOG,
                                 title='Senaite storage catalog',
                                 portal_meta_type='SenaiteStorageCatalog')

InitializeClass(SenaiteStorageCatalog)
