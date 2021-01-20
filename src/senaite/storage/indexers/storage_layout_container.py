# -*- coding: utf-8 -*-

from bika.lims.catalog.indexers import get_searchable_text_tokens
from plone.indexer import indexer
from senaite.storage.catalog import SENAITE_STORAGE_CATALOG
from senaite.storage.interfaces import ISenaiteStorageCatalog
from senaite.storage.interfaces import IStorageLayoutContainer


@indexer(IStorageLayoutContainer, ISenaiteStorageCatalog)
def listing_searchable_text(instance):
    """Add searchable text tokens for storage containers
    """
    entries = set()
    tokens = get_searchable_text_tokens(instance, SENAITE_STORAGE_CATALOG)
    entries.update(tokens)
    entries.update(instance.get_all_ids())
    return u" ".join(list(entries))
