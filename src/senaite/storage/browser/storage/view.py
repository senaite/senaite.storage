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
from bika.lims.utils import get_email_link
from bika.lims.utils import get_link
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.browser.storage.listing import StorageListing


class StorageListingView(StorageListing):
    """Listing view of all StorageFacilities
    """

    def __init__(self, context, request):
        super(StorageListingView, self).__init__(context, request)

        self.title = self.context.translate(_("Samples storage"))
        self.form_id = "list_storagerootfolder"

        self.contentFilter = {
            "portal_type": ["StorageFacility"],
            "sort_on": "path",
            "sort_order": "ascending"
        }

        # Add Facility action
        self.context_actions[_("Add Facility")] = {
            "url": "createObject?type_name=StorageFacility",
            "icon": "{}/{}".format(self.icon_path, "storage-facility")
        }

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Name"),
                "index": "sortable_index"}),
            ("SamplesUsage", {
                "title": _("Samples"),
            }),
            ("Samples", {
                "title": _("Samples usage"),
            }),
            ("Containers", {
                "title": _("Containers"),
            }),
            ("Phone", {
                "title": _("Phone"),
            }),
            ("EmailAddress", {
                "title": _("Email"),
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
                    "portal_type": [
                        "StorageFacility",
                        "StoragePosition",
                        "StorageContainer",
                        "StorageSamplesContainer",
                    ],
                    "sort_on": "path",
                    "review_state": "active",
                    "path": {
                        "query": api.get_path(context),
                    },
                },
                "confirm_transitions": ["recover_samples"],
                "columns": self.columns.keys(),
            }
        ]

    def folderitem(self, obj, item, index):
        """Applies new properties to item (StorageFacility) that is currently
        being rendered as a row in the list
        """
        item = super(StorageListingView, self).folderitem(obj, item, index)

        obj = api.get_object(obj)

        email = obj.getEmailAddress()
        if email:
            item["replace"]["EmailAddress"] = get_email_link(email)

        phone = obj.getPhone()
        if phone:
            item["replace"]["Phone"] = get_link("tel:{}".format(phone), phone)

        # Containers
        containers = obj.get_layout_containers()
        item["replace"]["Containers"] = "{:01d}".format(len(containers))

        return item
