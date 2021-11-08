# -*- coding: utf-8 -*-

from plone.indexer import indexer
from senaite.core.catalog.utils import get_searchable_text_tokens
from senaite.storage.catalog import SENAITE_STORAGE_CATALOG
from senaite.storage.interfaces import ISenaiteStorageCatalog
from senaite.storage.interfaces import IStoragePosition


@indexer(IStoragePosition, ISenaiteStorageCatalog)
def listing_searchable_text(instance):
    """Add searchable text tokens for storage positions
    """
    entries = set()
    tokens = get_searchable_text_tokens(instance, SENAITE_STORAGE_CATALOG)
    entries.update(tokens)
    return u" ".join(list(entries))
