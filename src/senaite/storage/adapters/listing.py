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

import copy

from bika.lims import api
from bika.lims import senaiteMessageFactory as _s
from senaite.app.listing import utils
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter
from senaite.core.api import dtime
from senaite.storage import is_installed
from senaite.storage import senaiteMessageFactory as _
from zope.component import adapter
from zope.interface import implementer

HIDE_COLUMNS = (
    "getAnalysesNum",
    "getDateVerified",
    "getDatePreserved",
    "getDatePublished",
    "getDueDate",
    "getStorageLocation",
    "Printed"
    "Progress",
    "SamplingDate",
)

ADD_COLUMNS = (
    {
        "id": "getDateStored",
        "title": _(
            u"listing_samples_column_date_stored",
            default=u"Date stored"
        ),
        "index": "getDateStored",
        "toggle": True,
        "after": "getDateReceived",
        "review_states": ("stored", "past_retention"),
    },
    {
        "id": "getStorageExpiryDate",
        "title": _(
            u"listing_samples_column_storage_expiry_date",
            default=u"Storage expiry date"
        ),
        "toggle": True,
        "after": "getDateStored",
        "review_states": ("stored", "past_retention"),
    },
    {
        "id": "getSamplesContainer",
        "title": _(
            u"listing_samples_column_storage",
            default=u"Storage"
        ),
        "attr": "getSamplesContainerID",
        "replace_url": "getSamplesContainerURL",
        "toggle": True,
        "after": "getDateStored",
        "review_states": ("stored", "past_retention"),
        "condition": "is_lab_user",
    }
)

ADD_CUSTOM_TRANSITIONS = (
    {
        "id": "print_stickers",
        "title": _s("Print stickers"),
        "url": "workflow_action?action=print_stickers",
        "review_states": ("stored", "past_retention")
    },
)

ADD_REVIEW_STATES = (
    {
        "id": "stored",
        "title": _(
            u"listing_samples_state_stored",
            default=u"Stored"
        ),
        "contentFilter": {
            "review_state": ("stored",),
            "sort_on": "created",
            "sort_order": "descending",
        },
        "confirm_transitions": ["recover"],
        "after": "published",
    },
    {
        "id": "past_retention",
        "title": _(
            u"listing_samples_state_past_retention",
            default=u"Past Retention"
        ),
        "contentFilter": {
            "review_state": ("stored",),
            "sort_on": "getDateStored",
            "sort_order": "descending",
        },
        "transitions": [],
        "confirm_transitions": ["recover"],
        "after": "stored",
    },
)


@adapter(IListingView)
@implementer(IListingViewAdapter)
class AnalysisRequestsListingViewAdapter(object):

    # Order of priority of this subscriber adapter over others
    priority_order = 10

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context
        self.installed = is_installed()
        self.flat_listing = False

    def before_render(self):
        # Return immediately if not installed
        if not self.installed:
            return

        # Additional filters/review statuses
        map(self.add_review_state, ADD_REVIEW_STATES)

        # Additional columns
        map(self.add_column, ADD_COLUMNS)

        # Additional custom transitions
        map(self.add_custom_transition, ADD_CUSTOM_TRANSITIONS)

        # In "stored" status, display all samples in "flat style"
        if self.is_stored_state():
            self.flat_listing = True
            self.listing.contentFilter.pop("isRootAncestor", None)

    def add_review_state(self, state_info):
        """Adds the review state with the provided information
        """
        info = copy.deepcopy(state_info)
        after = info.pop("after", None)
        cols = info.pop("columns", None)
        if not cols:
            cols = self.listing.columns.keys()
            cols = list(filter(lambda col: col not in HIDE_COLUMNS, cols))
        info["columns"] = cols
        utils.add_review_state(self.listing, info, after=after)

    def add_column(self, column_info):
        """Adds the column with the provided information
        """
        info = copy.deepcopy(column_info)
        condition = info.pop("condition", None)
        if condition and not getattr(self, condition)():
            # do not add the column if condition is not met
            return

        column_id = info.pop("id")
        after = info.pop("after", None)
        review_states = info.pop("review_states", None)
        if review_states is None:
            review_states = [st["id"] for st in self.listing.review_states]

        utils.add_column(listing=self.listing,
                         column_id=column_id,
                         column_values=info,
                         after=after,
                         review_states=review_states)

    def add_custom_transition(self, transition_info):
        """Adds a custom transition for the given statuses
        """
        info = copy.deepcopy(transition_info)
        statuses = info.pop("review_states")
        rss = filter(lambda a: a["id"] in statuses, self.listing.review_states)
        for rs in rss:
            rs.setdefault("custom_transitions", []).append(info)

    def is_lab_user(self):
        """Returns whether the current user is not from a client
        """
        if api.get_current_client():
            return False
        return True

    def folder_item(self, obj, item, index):
        # Return immediately when add-on is not installed
        if not self.installed:
            return item

        # Return immediately if sample is not stored
        if not self.is_stored_state():
            return item

        # date time when the sample was stored
        stored_date = dtime.to_localized_time(obj.getDateStored, long_format=1)
        item["getDateStored"] = stored_date

        # date when the retention period expires
        obj = api.get_object(obj)
        expiry_date = obj.getStorageExpiryDate()
        item["getStorageExpiryDate"] = dtime.to_localized_time(expiry_date)

        # display in red if retention expired
        if expiry_date <= dtime.DateTime():
            expiry = dtime.to_localized_time(expiry_date)
            span = "<span class='text-danger'>%s</span>" % expiry
            item["replace"]["getStorageExpiryDate"] = span

        return item

    def is_stored_state(self):
        """Returns whether the current review state of the listing is "stored"
        """
        review_state = self.listing.review_state
        if not review_state:
            return False
        statuses = [st["id"] for st in ADD_REVIEW_STATES]
        return review_state.get("id", "") in statuses
