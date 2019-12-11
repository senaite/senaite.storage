# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE.
#
# SENAITE.CORE.LISTING is free software: you can redistribute it and/or modify
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
# Copyright 2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from senaite.storage.interfaces import ISenaiteStorageCatalog
from zope.interface import implements

SENAITE_STORAGE_CATALOG = "senaite_storage_catalog"


class SenaiteStorageCatalog(BaseCatalog):
    implements(ISenaiteStorageCatalog)

    def __init__(self):
        BaseCatalog.__init__(self,
                             id=SENAITE_STORAGE_CATALOG,
                             title="Senaite storage catalog",
                             portal_meta_type="SenaiteStorageCatalog")


InitializeClass(SenaiteStorageCatalog)
