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
from senaite.storage import check_installed


@check_installed(None)
def getDateStored(self):
    """Returns the date the sample was stored
    """
    return wf.getTransitionDate(self, "store") or None


@check_installed(None)
def getDateBookedOut(self):
    """Returns the date the sample was booked out
    """
    return wf.getTransitionDate(self, "book_out") or None


@check_installed(None)
def getBookOutReason(self):
    """Returns the review history comment for the sample book out
    """
    if api.get_review_status(self) != "booked_out":
        return ""
    history = api.get_review_history(self)
    entry = history[0]
    return api.safe_unicode(entry.get("comments", ""))


@check_installed(None)
def getBookOutActor(self):
    """Returns the review history comment for the sample book out
    """
    if api.get_review_status(self) != "booked_out":
        return ""
    history = api.get_review_history(self)
    entry = history[0]
    return api.safe_unicode(entry.get("actor", ""))


@check_installed(None)
def getSamplesContainer(self):
    """Returns the samples container the sample is located in
    """
    return _api.get_storage_sample(self)


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
