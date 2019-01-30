# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

import collections

from bika.lims import api
from bika.lims.api import get_icon
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.utils import get_link, get_progress_bar_html
from senaite.storage import senaiteMessageFactory as _


class SamplesListing(BikaListingView):
    """Listing view of sample objects from inside storage
    """

    def __init__(self, context, request):
        super(SamplesListing, self).__init__(context, request)
        request.set("disable_border", 1)
        self.title = context.Title()
        self.form_id = "list_storage_samples"
        self.sort_on = "sortable_title"
        self.show_select_row = False
        self.show_select_all_checkboxes = False
        self.show_select_column = False
        self.catalog = CATALOG_ANALYSIS_REQUEST_LISTING
        self.contentFilter = {
            "UID": context.get_samples_uids(),
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        }

        self.columns = collections.OrderedDict((
            ("getId", {
                "title": _("Sample ID"),
                "attr": "getId",
                "replace_url": "getURL",
                "index": "getId"}),
            ("getDateSampled", {
                "title": _("Date Sampled"),
                "toggle": True}),
            ("getDateReceived", {
                "title": _("Date Received"),
                "toggle": False}),
            ("Client", {
                "title": _("Client"),
                "index": "getClientTitle",
                "attr": "getClientTitle",
                "replace_url": "getClientURL",
                "toggle": True}),
            ("getClientReference", {
                "title": _("Client Ref"),
                "sortable": True,
                "index": "getClientReference",
                "toggle": False}),
            ("getClientSampleID", {
                "title": _("Client SID"),
                "toggle": False}),
            ("getSampleTypeTitle", {
                "title": _("Sample Type"),
                "sortable": True,
                "toggle": True}),
        ))

        self.review_states = [
            {
                "id": "default",
                "contentFilter": {},
                "title": _("All"),
                "transitions": [],
                "columns": self.columns.keys(),
            },
        ]

        imgs_path = "++resource++senaite.storage.static/img"
        self.icon = "{}/{}/{}".format(self.portal_url, imgs_path, "box_big.png")
        if not context.is_full():
            uid = api.get_uid(context)
            self.context_actions = collections.OrderedDict()
            self.context_actions[_("Add Samples")] = {
                "url": "storage_store_samplescontainer?uid={}".format(uid),
                "icon": "{}/{}".format(
                    self.portal_url, "/++resource++bika.lims.images/sample.png")
            }

    def folderitems(self, full_objects=False, classic=False):
        """We add this function to tell baselisting to use brains instead of
        full objects"""
        return BikaListingView.folderitems(self, full_objects, classic)

    def folderitem(self, obj, item, index):
        """Applies new properties to item that is currently being rendered as a
        row in the list
        """
        received = obj.getDateReceived
        sampled = obj.getDateSampled
        item["getDateReceived"] = self.ulocalized_time(received, long_format=1)
        item["getDateSampled"] = self.ulocalized_time(sampled, long_format=1)
        return item
