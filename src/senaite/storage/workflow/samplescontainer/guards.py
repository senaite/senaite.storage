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
# Copyright 2019-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl.SecurityInfo import ModuleSecurityInfo
from senaite.storage.interfaces import IStorageSamplesContainer

security = ModuleSecurityInfo(__name__)

@security.public
def guard_recover_samples(samples_container):
    """ Guard for recover all samples from this container
    """
    if not IStorageSamplesContainer.providedBy(samples_container):
        return False
    return samples_container.has_samples()


@security.public
def guard_add_samples(samples_container):
    """Guard for adding samples to this container
    """
    if not IStorageSamplesContainer.providedBy(samples_container):
        return False
    return not samples_container.is_full()
