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

from plone.indexer import indexer
from senaite.core.catalog.utils import get_searchable_text_tokens
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.interfaces import ISenaiteStorageCatalog
from senaite.storage.interfaces import IStorageLayoutContainer


@indexer(IStorageLayoutContainer, ISenaiteStorageCatalog)
def listing_searchable_text(instance):
    """Add searchable text tokens for storage containers
    """
    entries = set()
    tokens = get_searchable_text_tokens(instance, STORAGE_CATALOG)
    entries.update(tokens)
    entries.update(instance.get_all_ids())
    return u" ".join(list(entries))
