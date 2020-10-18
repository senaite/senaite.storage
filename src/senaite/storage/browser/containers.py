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
from bika.lims.utils import get_progress_bar_html
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.browser.storagelisting import StorageListing
from senaite.storage.interfaces import IStorageContainer
from senaite.storage.interfaces import IStorageSamplesContainer


class ContainersView(StorageListing):
    """Listing view of all StorageContainers
    """

    def __init__(self, context, request):
        super(ContainersView, self).__init__(context, request)
        self.title = context.Title()
        self.form_id = "list_storage_containers"
        self.show_select_column = True
        self.contentFilter = {
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": "/".join(context.getPhysicalPath()),
                "depth": 1,
            }
        }

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Name"),
                "index": "sortable_index"}),
            ("Id", {
                "title": _("ID")}),
            ("Temperature", {
                "title": _("Temperature"),}),
            ("SamplesUsage", {
                "title": _("Samples"),}),
            ("Samples", {
                "title": _("Samples usage"),}),
            ("ContainersUsage", {
                "title": _("Containers"),}),
            ("Containers", {
                "title": _("Containers usage"),}),
        ))

        self.review_states = [{
                "id": "default",
                "contentFilter": {"review_state": "active"},
                "title": _("Top-level"),
                "transitions": [],
                "confirm_transitions": ["recover_samples"],
                "columns": self.columns.keys(),
            }, {
                "id": "full",
                "contentFilter": {
                    "sort_on": "path",
                    "review_state": "active",
                    "path": {
                        "query": "{}/".format("/".join(context.getPhysicalPath())),
                    },
                },
                "title": _("Full hierarchy"),
                "transitions": [],
                "confirm_transitions": ["recover_samples"],
                "columns": self.columns.keys(),
            }
        ]

        ico_path = "{}/senaite_theme/icon/".format(self.portal_url)

        self.context_actions = collections.OrderedDict()
        if not IStorageSamplesContainer.providedBy(self.context):
            self.context_actions[_("Add container")] = {
                "url": "createObject?type_name=StorageContainer",
                "icon": "{}/{}".format(ico_path, "storage-container")
            }

        if IStorageContainer.providedBy(self.context):
            self.context_actions[_("Add samples container")] = {
                "url": "createObject?type_name=StorageSamplesContainer",
                "icon": "{}/{}".format(ico_path, "storage-sample-container")
            }

    def folderitem(self, obj, item, index):
        """Applies new properties to item (StorageContainer) that is currently
        being rendered as a row in the list
        """
        item = super(ContainersView, self).folderitem(obj, item, index)

        # Get the object (the passed-in "obj" is a brain)
        obj = api.get_object(obj)

        # Containers/Positions usage
        # Samples containers cannot have containers inside!
        if not IStorageSamplesContainer.providedBy(obj):
            capacity = obj.get_capacity()
            taken = len(obj.get_non_available_positions())
            percentage = capacity and taken*100/capacity or 0
            item["replace"]["ContainersUsage"] = get_progress_bar_html(percentage)
            item["replace"]["Containers"] = "{:01d} / {:01d} ({:01d}%)"\
                .format(taken, capacity, percentage)

        if self.review_state.get("id") == "full":
            # Display full hierarchy
            parent = api.get_path(obj)
            curr_path = api.get_path(self.context)
            path = parent.replace(curr_path, "")
            parts = filter(None, path.split("/"))
            if len(parts) > 1:
                prefix = "&emsp;"*(len(parts)-1)
                text = "".join([prefix, item["before"]["Title"]])
                item["before"]["Title"] = text

        return item

    def isItemAllowed(self, obj):
        if self.review_state.get("id") == "full":
            # Do not display current context in the listing
            return api.get_id(obj) != api.get_id(self.context)
        return True
