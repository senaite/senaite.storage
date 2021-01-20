# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.storage.interfaces import IStorageLayoutContainer
from senaite.storage.interfaces import IStorageUtilization
from zope.interface import implementer


@implementer(IStorageUtilization)
class StorageUtilization(object):

    def __init__(self, context):
        self.context = context

    def get_capacity(self):
        """Returns the total number of containers
        """
        return len(self.get_layout_containers())

    def get_available_positions(self):
        """Returns the number of available containers
        """
        return self.get_capacity()

    def get_layout_containers(self):
        """Returns the contained containers
        """
        query = {"path": {"query": api.get_path(self.context)}}
        brains = api.search(query)
        objs = map(api.get_object, brains)
        return filter(lambda ob: IStorageLayoutContainer.providedBy(ob), objs)

    def get_samples_capacity(self):
        """Returns the total sample capacity
        """
        containers = self.get_layout_containers()
        return sum(map(lambda con: con.get_samples_capacity(), containers))

    def get_samples_utilization(self):
        """Returns the total number of samples
        """
        containers = self.get_layout_containers()
        return sum(map(lambda con: con.get_samples_utilization(), containers))
