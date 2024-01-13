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
from bika.lims.interfaces import IGuardAdapter
from senaite.storage.interfaces import IStorageContainer
from senaite.storage.interfaces import IStorageSamplesContainer
from zope.interface import implementer


@implementer(IGuardAdapter)
class GuardsAdapter(object):
    """Baseline class for guard adapters
    """

    def __init__(self, context):
        self.context = context

    def guard(self, action):
        func_name = "guard_{}".format(action)
        func = getattr(self, func_name, None)
        if func:
            return func(self.context)

        # No guard intercept here
        return True

    def guard_add_samples(self, context):
        """Guard for adding samples to this container
        """
        if not IStorageSamplesContainer.providedBy(context):
            return False
        return not context.is_full()

    def guard_recover_samples(self, context):
        """Guard for recover all samples from this container
        """
        if not IStorageSamplesContainer.providedBy(context):
            return False
        return context.has_samples()

    def guard_move_container(self, context):
        """Guard for move container
        """
        if not api.is_active(context):
            return False
        if IStorageContainer.providedBy(context):
            return True
        if IStorageSamplesContainer.providedBy(context):
            return True
        return False
