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
