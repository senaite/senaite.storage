# -*- coding: utf-8 -*-

from plone.indexer import indexer
from senaite.core.catalog.utils import get_searchable_text_tokens
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.interfaces import ISenaiteStorageCatalog
from senaite.storage.interfaces import IStorageFacility


@indexer(IStorageFacility, ISenaiteStorageCatalog)
def listing_searchable_text(instance):
    """Add searchable text tokens for storage facilities
    """
    entries = set()
    tokens = get_searchable_text_tokens(instance, STORAGE_CATALOG)
    entries.update(tokens)
    return u" ".join(list(entries))
