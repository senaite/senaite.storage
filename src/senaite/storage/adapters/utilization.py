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

from bika.lims import api
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.interfaces import IStorageSamplesContainer
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
        # return immediately if the container is a
        if IStorageSamplesContainer.providedBy(self.context):
            return [self.context]
        query = {
            "review_state": "active",
            "path": {
                "query": api.get_path(self.context),
            }}
        brains = api.search(query, STORAGE_CATALOG)
        objs = map(api.get_object, brains)
        return filter(lambda o: IStorageSamplesContainer.providedBy(o), objs)

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
