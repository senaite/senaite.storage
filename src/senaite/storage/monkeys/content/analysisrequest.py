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
from bika.lims import workflow as wf
from senaite.storage import api as sapi
from senaite.storage import check_installed


@check_installed(None)
def getDateStored(self):
    """Returns the date the sample was stored
    """
    return wf.getTransitionDate(self, "store") or None


@check_installed(None)
def getSamplesContainer(self):
    """Returns the samples container the sample is located in
    """
    return sapi.get_storage_sample(self)


@check_installed(None)
def getSamplesContainerID(self):
    """Returns the ID of the samples container the sample is located in
    """
    container = getSamplesContainer(self)
    return container and api.get_id(container) or ""


@check_installed(None)
def getSamplesContainerURL(self):
    """Returns the URL of the samples container the sample is located in
    """
    container = getSamplesContainer(self)
    return container and api.get_url(container) or ""


@check_installed(None)
def getStorageRetentionPeriod(self):
    """Returns the retention period (days) assigned during storage
    """
    field = self.getField("StorageRetentionPeriod")
    return field.get(self)


@check_installed(None)
def setStorageRetentionPeriod(self, days):
    """Sets the retention period (days) for storage
    """
    field = self.getField("StorageRetentionPeriod")
    days = api.to_int(days, default=None)
    field.set(self, days)


@check_installed(None)
def getDefaultStorageRetentionPeriod(self):
    """Returns the default retention period (days) computed from rules
    """
    return sapi.get_default_retention_period(self)
