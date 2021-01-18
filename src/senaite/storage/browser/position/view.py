# -*- coding: utf-8 -*-

from senaite.storage.browser.facility.view import FacilityListingView


class PositionListingView(FacilityListingView):
    """Listing view for a storage position
    """

    def __init__(self, context, request):
        super(PositionListingView, self).__init__(context, request)

        self.icon = "{}/{}".format(
            self.portal_url, "senaite_theme/icon/storage-position")
