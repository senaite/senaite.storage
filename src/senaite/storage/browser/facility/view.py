# -*- coding: utf-8 -*-

import collections

from bika.lims import api
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.browser.storage.listing import StorageListing


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
                "permission": "cmf.AddPortalContent",
                "icon": "{}/{}".format(self.icon_path, "storage-position"),
            }),
            (_("Add container"), {
                "url": "createObject?type_name=StorageContainer",
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
        """Applies new properties to item (StorageContainer) that is currently
        being rendered as a row in the list
        """
        item = super(FacilityListingView, self).folderitem(obj, item, index)
        return item
