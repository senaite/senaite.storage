# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.storage.browser.facility.view import FacilityListingView


class PositionListingView(FacilityListingView):
    """Listing view for a storage position
    """

    def __init__(self, context, request):
        super(PositionListingView, self).__init__(context, request)

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

        self.icon = "{}/{}".format(
            self.portal_url, "senaite_theme/icon/storage-position")
