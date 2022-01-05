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

from bika.lims.interfaces import IBikaLIMS
from senaite.core.interfaces import ISenaiteCatalogObject
from senaite.lims.interfaces import ISenaiteLIMS
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager


class ISenaiteStorageLayer(IBikaLIMS, ISenaiteLIMS):
    """Zope 3 browser Layer interface specific for senaite.storage
    This interface is referred in profiles/default/browserlayer.xml.
    All views and viewlets register against this layer will appear in the site
    only when the add-on installer has been run.
    """


class ISenaiteStorageCatalog(ISenaiteCatalogObject):
    """Marker interface for senaite_storage_catalog CatalogTool
    """


class IStorageContent(Interface):
    """Marker interface for all storage contents
    """


class IStorageRootFolder(IStorageContent):
    """Marker interface for Storage's root folders
    """


class IStorageFacility(IStorageContent):
    """Marker interface for objects that represent a physical location or place
    where one or more storage containers are located. (room, department, etc.)
    """


class IStoragePosition(IStorageContent):
    """Marker interface for objects that describe the position inside a facility
    """


class IStorageLayoutContainer(IStorageContent):
    """Marker interface for objects that act as containers, either of other
    containers or other type of objects such as samples. All these objects have
    layout field in common in which the positions where the stored elements are
    defined.
    """


class IStorageContainer(IStorageContent):
    """Marker interface for objects that represent an storage container designed
    for the storage of one or more than one elements inside, typically other
    containers. E.g: fridge, rack, shelf, floating rack, tube rack, box, etc.
    """


class IStorageSamplesContainer(IStorageContent):
    """Marker interface for objects that represent a type of storage container
    designed for the storage of multiple samples (storage box, tube rack, etc.)
    """


class IStorageJS(IViewletManager):
    """A viewlet manager that provides the JavaScripts for DataBox
    """


class IStorageBreadcrumbs(Interface):
    """Adapter to provide the storage breadcrumbs
    """

    def get_storage_breadcrumbs(breadcrumbs=None):
        """Generate a breadcrumbs like title
        """


class IStorageUtilization(Interface):
    """Adapter to provide storage utilization details
    """

    def get_capacity():
        """Returns the total number of containers
        """

    def get_available_positions():
        """Returns the number of available containers
        """

    def get_layout_containers():
        """Returns the contained containers
        """

    def get_samples_capacity():
        """Returns the total sample capacity
        """

    def get_samples_utilization():
        """Returns the total number of samples
        """
