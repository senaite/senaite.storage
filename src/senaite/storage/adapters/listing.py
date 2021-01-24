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
from senaite.app.listing import utils
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter
from senaite.storage import is_installed
from senaite.storage import senaiteMessageFactory as _
from zope.component import adapts
from zope.interface import implementer


@implementer(IListingViewAdapter)
class AnalysisRequestsListingViewAdapter(object):
    adapts(IListingView)

    # Order of priority of this subscriber adapter over others
    priority_order = 10

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context
        self.installed = is_installed()
        self.flat_listing = False

    def before_render(self):
        if not self.installed:
            return

        # Add review state "stored" in the listing
        self.add_stored_review_state()

        # Add review state "booked out" in the listing
        self.add_booked_out_review_state()

        # In "stored" status, display all samples in "flat style"
        if self.is_stored_state():
            self.flat_listing = True

        # In "booked_out" status, display all samples in "flat style"
        if self.is_booked_out_state():
            self.flat_listing = True

        if self.flat_listing:
            if "isRootAncestor" in self.listing.contentFilter:
                del self.listing.contentFilter["isRootAncestor"]

    def add_stored_review_state(self):
        """Adds the "stored" review state to the listing's review_states pool
        """
        # Columns to hide
        hide = [
            "getAnalysesNum",
            "getDateVerified",
            "getDatePreserved",
            "getDatePublished",
            "getDueDate",
            "getStorageLocation",
            "Printed"
            "Progress",
            "SamplingDate",
        ]
        columns = filter(lambda c: c not in hide, self.listing.columns.keys())

        # Custom transitions
        print_stickers = {
            "id": "print_stickers",
            "title": _("Print stickers"),
            "url": "workflow_action?action=print_stickers"
        }

        # "stored" review state
        stored = {
            "id": "stored",
            "title": _("Stored"),
            "contentFilter": {
                "review_state": ("stored",),
                "sort_on": "created",
                "sort_order": "descending",
            },
            "transitions": [],
            "custom_transitions": [print_stickers],
            "confirm_transitions": ["recover"],
            "columns": columns,
        }

        # Add the review state
        utils.add_review_state(self.listing, stored, after="published")

        # Add the column "DateStored" to "stored" review_state
        column_values = {
            "title": _("Date stored"),
            "index": "getDateStored",
            "toggle": True}
        utils.add_column(self.listing, "getDateStored", column_values,
                         after="getDateReceived", review_states=("stored",))

        # Add Samples Container column, but only if the current user logged in
        # is not a client contact
        if not api.get_current_client():
            column_values = {
                "title": _("Storage"),
                "attr": "getSamplesContainerID",
                "replace_url": "getSamplesContainerURL",
                "toggle": True
            }
            utils.add_column(self.listing, "getSamplesContainer",
                             column_values, after="getDateStored",
                             review_states=("stored", ))

    def add_booked_out_review_state(self):
        """Adds the "booked_out" review state to the listing's review_states pool
        """
        # Columns to hide
        hide = [
            "getAnalysesNum",
            "getDateVerified",
            "getDatePreserved",
            "getDatePublished",
            "getDueDate",
            "getStorageLocation",
            "Printed"
            "Progress",
            "SamplingDate",
            "getSamplesContainer",
        ]
        columns = filter(lambda c: c not in hide, self.listing.columns.keys())

        # Custom transitions
        print_stickers = {
            "id": "print_stickers",
            "title": _("Print stickers"),
            "url": "workflow_action?action=print_stickers"
        }

        # "booked_out" review state
        stored = {
            "id": "booked_out",
            "title": _("Booked out"),
            "contentFilter": {
                "review_state": ("booked_out",),
                "sort_on": "created",
                "sort_order": "descending",
            },
            "transitions": [],
            "custom_transitions": [print_stickers],
            "confirm_transitions": ["recover"],
            "columns": columns,
        }

        # Add the review state
        utils.add_review_state(self.listing, stored, after="stored")

        # Add the column "getDateBookedOut" to "booked_out" review_state
        column_values = {
            "title": _("Book out date"),
            "index": "getDateBookedOut",
            "toggle": True}
        utils.add_column(
            self.listing, "getDateBookedOut", column_values,
            after="getDateStored", review_states=("booked_out",))

        # Add the column "getBookOutReason" to "booked_out" review_state
        column_values = {
            "title": _("Book out reason"),
            "toggle": True}
        utils.add_column(
            self.listing, "getBookOutReason", column_values,
            after="getDateBookedOut", review_states=("booked_out",))

        # Add the column "getBookOutActor" to "booked_out" review_state
        column_values = {
            "title": _("Booked out by"),
            "index": "getBookOutActor",
            "toggle": True}
        utils.add_column(
            self.listing, "getBookOutActor", column_values,
            after="getBookOutReason", review_states=("booked_out",))

    def folder_item(self, obj, item, index):
        # Return immediately when add-on is not installed
        if not self.installed:
            return item

        # Ingore partitions and add column
        if self.is_stored_state():
            # Show the date time when the sample was stored
            item["getDateStored"] = self.str_time(obj.getDateStored)

        if self.is_booked_out_state():
            # Show the date time when the sample was stored
            item["getDateBookedOut"] = self.str_time(obj.getDateBookedOut)
            item["getBookOutReason"] = obj.getBookOutReason
            item["getBookOutActor"] = obj.getBookOutActor

        # Display all samples in "flat style"
        if self.flat_listing:
            item["parent"] = ""
            item["children"] = []

        return item

    def str_time(self, date_time, long_format=1):
        """Returns a string representation of localized DateTime
        """
        return self.listing.ulocalized_time(date_time, long_format=long_format)

    def is_stored_state(self):
        """Returns whether the current review state of the listing is "stored"
        """
        review_state = self.listing.review_state
        if not review_state:
            return False
        return review_state.get("id", "") == "stored"

    def is_booked_out_state(self):
        """Returns whether the current review state of the listing is "booked_out"
        """
        review_state = self.listing.review_state
        if not review_state:
            return False
        return review_state.get("id", "") == "booked_out"
