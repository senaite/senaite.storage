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

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _s
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from senaite.storage import senaiteMessageFactory as _


class SamplesListing(BikaListingView):
    """Listing view of sample objects from inside storage
    """

    def __init__(self, context, request):
        super(SamplesListing, self).__init__(context, request)
        request.set("disable_sorder", 1)
        self.title = context.Title()
        self.form_id = "list_storage_samples"
        self.sort_on = "sortable_title"
        self.show_select_row = False
        self.show_select_all_checkboxes = False
        self.show_select_column = True
        self.catalog = CATALOG_ANALYSIS_REQUEST_LISTING
        self.contentFilter = {
            "UID": context.get_samples_uids(),
            "sort_on": "sortable_title",
            "sort_order": "ascending"
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
        ))

        self.review_states = [
            {
                "id": "default",
                "contentFilter": {},
                "title": _s("All"),
                "transitions": [],
                "columns": self.columns.keys(),
            },
        ]

        imgs_path = "++resource++senaite.storage.static/img"
        self.icon = "{}/{}/{}".format(self.portal_url, imgs_path, "box_big.png")
        self.context_actions = collections.OrderedDict()
        if not context.is_full():
            uid = api.get_uid(context)
            self.context_actions[_("Add Samples")] = {
                "url": "storage_store_container?uids={}".format(uid),
                "icon": "{}/{}".format(
                    self.portal_url, "/++resource++bika.lims.images/sample.png")
            }

    def folderitems(self):
        """We add this function to tell baselisting to use brains instead of
        full objects"""
        items = BikaListingView.folderitems(self)
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
        item["position"] = self.context.position_to_alpha(position[0], position[1])
        return item
