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

from bika.lims import api
from bika.lims import workflow as wf
from senaite.storage import api as _api


def getDateStored(self):
    """Returns the date the sample was stored
    """
    return wf.getTransitionDate(self, "store") or None


def getSamplesContainer(self):
    """Returns the samples container the sample is located in
    """
    return _api.get_storage_sample(self)


def getSamplesContainerID(self):
    """Returns the ID of the samples container the sample is located in
    """
    container = getSamplesContainer(self)
    return container and api.get_id(container) or ""


def getSamplesContainerURL(self):
    """Returns the URL of the samples container the sample is located in
    """
    container = getSamplesContainer(self)
    return container and api.get_url(container) or ""
