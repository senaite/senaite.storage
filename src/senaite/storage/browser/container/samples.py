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

import collections

from bika.lims import api
from bika.lims import senaiteMessageFactory as _s
from senaite.app.listing.view import ListingView
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.permissions import TransitionAddSamples


class SampleListingView(ListingView):
    """Listing view of sample objects from inside storage
    """

    def __init__(self, context, request):
        super(SampleListingView, self).__init__(context, request)

        self.catalog = SAMPLE_CATALOG

        self.contentFilter = {
            "UID": context.get_samples_uids(),
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        }

        self.form_id = "list_storage_samples"
        self.show_select_all_checkbox = True
        self.show_select_column = True
        self.sort_on = "sortable_title"
        self.title = context.Title()
        self.description = context.Description()
        self.icon_path = "{}/senaite_theme/icon/".format(self.portal_url)

        if not context.is_full():
            uid = api.get_uid(context)
            self.context_actions[_("Add Samples")] = {
                "url": "storage_store_container?uids={}".format(uid),
                "permission": TransitionAddSamples,
                "icon": "{}/{}".format(self.icon_path, "sample")
            }

        self.columns = collections.OrderedDict((
            ("position", {
                "title": _("Position"),
                "sortable": True,
                "toggle": True}),
            ("getId", {
                "title": _s("Sample ID"),
                "attr": "getId",
                "replace_url": "getURL",
                "index": "getId"}),
            ("getDateSampled", {
                "title": _s("Date Sampled"),
                "toggle": True}),
            ("getDateReceived", {
                "title": _s("Date Received"),
                "toggle": True}),
            ("Client", {
                "title": _s("Client"),
                "index": "getClientTitle",
                "attr": "getClientTitle",
                "replace_url": "getClientURL",
                "toggle": True}),
            ("getClientReference", {
                "title": _s("Client Ref"),
                "sortable": True,
                "index": "getClientReference",
                "toggle": False}),
            ("getClientSampleID", {
                "title": _s("Client SID"),
                "toggle": False}),
            ("getSampleTypeTitle", {
                "title": _s("Sample Type"),
                "sortable": True,
                "toggle": True}),
            ("PreviousState", {
                "title": _s("Previous State"),
                "sortable": True,
                "toggle": True}),
        ))

        self.review_states = [
            {
                "id": "default",
                "contentFilter": {},
                "title": _s("All"),
                "transitions": [],
                "confirm_transitions": ["recover"],
                "columns": self.columns.keys(),
            },
        ]

    def before_render(self):
        super(SampleListingView, self).before_render()
        # show message if full
        if self.context.is_full():
            message = _("Container is full")
            self.add_status_message(message, level="warning")
        else:
            context = self.context
            capacity = context.get_samples_capacity()
            utilization = context.get_samples_utilization()
            message = _("Container utilization {} / {}".format(
                utilization, capacity))
            self.add_status_message(message, level="info")

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def folderitems(self):
        """We add this function to tell baselisting to use brains instead of
        full objects"""
        items = super(SampleListingView, self).folderitems()
        return sorted(items, key=lambda item: item["position"])

    def folderitem(self, obj, item, index):
        """Applies new properties to item that is currently being rendered as a
        row in the list
        """
        received = obj.getDateReceived
        sampled = obj.getDateSampled
        item["getDateReceived"] = self.ulocalized_time(received, long_format=1)
        item["getDateSampled"] = self.ulocalized_time(sampled, long_format=1)
        position = self.context.get_object_position(api.get_uid(obj))
        item["position"] = self.context.position_to_alpha(
            position[0], position[1])
        prev_state = api.get_previous_worfklow_status_of(obj, skip=("stored",))
        if prev_state:
            item["PreviousState"] = self.translate_review_state(
                prev_state, api.get_portal_type(obj))
        return item
