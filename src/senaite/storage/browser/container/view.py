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
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.browser.facility.view import FacilityListingView
from senaite.storage.permissions import AddStorageContainer
from senaite.storage.permissions import AddStorageSamplesContainer


class ContainerListingView(FacilityListingView):
    """Listing view of all Storage- and Sample Containers
    """

    def __init__(self, context, request):
        super(ContainerListingView, self).__init__(context, request)

        self.contentFilter = {
            "portal_type": [
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

        self.form_id = "list_storage_containers"

        self.context_actions = collections.OrderedDict((
            (_("Add container"), {
                "url": "createObject?type_name=StorageContainer",
                "permission": AddStorageContainer,
                "icon": "{}/{}".format(
                    self.icon_path, "storage-container"),
            }),
            (_("Add samples container"), {
                "url": "createObject?type_name=StorageSamplesContainer",
                "permission": AddStorageSamplesContainer,
                "icon": "{}/{}".format(
                    self.icon_path, "storage-sample-container")
            }),
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
        item = super(ContainerListingView, self).folderitem(obj, item, index)
        return item
