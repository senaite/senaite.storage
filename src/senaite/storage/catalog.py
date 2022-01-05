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

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog as OldBaseCatalog
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.storage.interfaces import ISenaiteStorageCatalog
from zope.interface import implements

CATALOG_ID = "senaite_catalog_storage"
STORAGE_CATALOG = CATALOG_ID  # for imports
CATALOG_TITLE = "Senaite Storage Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type

    # Ids of parent containers and current
    ("get_all_ids", "", "KeywordIndex"),
    # Keeps the sample uids stored in each sample container
    ("get_samples_uids", "", "KeywordIndex"),
    # For searches, made of get_all_ids + Title
    ("listing_searchable_text", "", "ZCTextIndex"),
    # Index used in searches to filter sample containers with available slots
    ("Title", "", "FieldIndex"),
    ("is_full", "", "BooleanIndex"),
    ("sortable_title", "", "FieldIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "id",
    "Title",
    "Description",
]

TYPES = [
    # portal_type name
    "StorageFacility",
    "StoragePosition",
    "StorageContainer",
    "StorageSamplesContainer",
]


class StorageCatalog(BaseCatalog):
    implements(ISenaiteStorageCatalog)

    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)


class SenaiteStorageCatalog(OldBaseCatalog):
    """BBB: Remove after 2.1.0 migration
    """


InitializeClass(StorageCatalog)
InitializeClass(SenaiteStorageCatalog)
