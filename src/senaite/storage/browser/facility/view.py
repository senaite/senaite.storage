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
from bika.lims.utils import get_link_for
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.api import get_parents
from senaite.storage.browser.storage.listing import StorageListing
from senaite.storage.interfaces import IStorageFacility
from senaite.storage.permissions import AddStorageContainer
from senaite.storage.permissions import AddStoragePosition


class FacilityListingView(StorageListing):
    """Listing view for a storage facility
    """

    def __init__(self, context, request):
        super(FacilityListingView, self).__init__(context, request)

        self.contentFilter = {
            "portal_type": [
                "StoragePosition",
                "StorageContainer",
                "StorageSamplesContainer",
            ],
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(context),
                "depth": 1,
            }
        }

        self.form_id = "facility_listing"

        self.context_actions = collections.OrderedDict((
            (_("Add storage position"), {
                "url": "++add++StoragePosition",
                "permission": AddStoragePosition,
                "icon": "{}/{}".format(self.icon_path, "storage-position"),
            }),
            (_("Add container"), {
                "url": "createObject?type_name=StorageContainer",
                "permission": AddStorageContainer,
                "icon": "{}/{}".format(self.icon_path, "storage-container"),
            }),
        ))

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Name"),
                "index": "sortable_title"}),
            ("Id", {
                "title": _("ID")}),
            ("SamplesUsage", {
                "title": _("% Samples")}),
            ("Samples", {
                "title": _("Samples")}),
            ("Description", {
                "title": _("Description")}),
            ("Position", {
                "title": _("Position")}),
            ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Collapsed"),
                "contentFilter": {"review_state": "active"},
                "confirm_transitions": ["recover_samples"],
                "columns": self.columns.keys(),
            }, {
                "id": "expand",
                "title": _("Expanded"),
                "contentFilter": {
                    "sort_on": "path",
                    "review_state": "active",
                    "path": {
                        "query": api.get_path(context),
                    },
                },
                "confirm_transitions": ["recover_samples"],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {"review_state": "inactive"},
                "confirm_transitions": ["recover_samples"],
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        """Applies new properties to item (StorageContainer) that is currently
        being rendered as a row in the list
        """
        item = super(FacilityListingView, self).folderitem(obj, item, index)
        obj = api.get_object(obj)
        parents = get_parents(
            obj, predicate=lambda o: IStorageFacility.providedBy(o))
        item["replace"]["Position"] = " » ".join(
            map(get_link_for, reversed(parents)))
        return item
