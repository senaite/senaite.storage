# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.storage.interfaces import IStorageBreadcrumbs
from senaite.storage.interfaces import IStorageFacility
from zope.interface import implementer


@implementer(IStorageBreadcrumbs)
class StorageBreadcrumbs(object):

    def __init__(self, context):
        self.context = context

    def get_storage_breadcrumbs(self, breadcrumbs=None):
        """Returns the full title of this container in breadcrumbs format
        """
        if not breadcrumbs:
            breadcrumbs = "{} - {}".format(
                api.get_title(self.context), api.get_id(self.context))
        parent = api.get_parent(self.context)
        breadcrumbs = "{} > {}".format(api.get_title(parent), breadcrumbs)
        if IStorageFacility.providedBy(parent):
            return breadcrumbs
        adapter = IStorageBreadcrumbs(parent)
        return adapter.get_storage_breadcrumbs(breadcrumbs)
