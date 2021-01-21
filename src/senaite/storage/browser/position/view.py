# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.browser.facility.view import FacilityListingView


class PositionListingView(FacilityListingView):
    """Listing view for a storage position
    """

    def __init__(self, context, request):
        super(PositionListingView, self).__init__(context, request)

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

        self.form_id = "position_listing"

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
            }
        ]

    def isItemAllowed(self, obj):
        """Skip own container
        """
        return api.get_uid(obj) != api.get_uid(self.context)
