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
# Copyright 2019-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from senaite.storage.interfaces import IStorageContainer
from senaite.storage.interfaces import IStorageSamplesContainer
from senaite.storage.workflow.guard import GuardAdapter


class StorageGuardAdapter(GuardAdapter):
    """Guards adapter for SamplesContainer
    """

    def guard_move_container(self):
        """Guard for move container
        """
        container = self.context
        if not api.is_active(container):
            return False
        if IStorageContainer.providedBy(container):
            return True
        if IStorageSamplesContainer.providedBy(container):
            return True
        return False
