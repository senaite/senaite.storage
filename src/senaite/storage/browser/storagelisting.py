# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

import collections

from bika.lims import api
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_link, get_email_link, get_progress_bar_html
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.interfaces import IStorageFacility, \
    IStorageSamplesContainer


class StorageListing(BikaListingView):
    """Listing view of storage-like objects
    """

    def __init__(self, context, request):
        super(StorageListing, self).__init__(context, request)
        self.sort_on = "sortable_title"
        self.show_select_row = False
        self.show_select_all_checkboxes = False
        self.show_select_column = False
        request.set("disable_border", 1)

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Name"),
                "index": "sortable_index"}),
            ("Usage", {
                "title": _("Usage"),}),
            ("Samples", {
                "title": _("Samples"),}),
            ("Capacity", {
                "title": _("Capacity"),}),
        ))

        self.review_states = [
            {
                "id": "default",
                "contentFilter": {"review_state": "active"},
                "title": _("Active"),
                "transitions": [],
                "columns": self.columns.keys(),
            },
        ]

    def get_usage_bar_html(self, percentage):
        """Returns an html that represents an usage bar
        """
        css_class = "bg-success"
        if percentage > 90:
            css_class = "bg-danger"
        elif percentage > 75:
            css_class = "bg-warning"
        progress_bar = get_progress_bar_html(percentage)
        return progress_bar.replace('class="progress-bar',
                                    'class="progress-bar {}'.format(css_class))

    def folderitem(self, obj, item, index):
        """Applies new properties to item that is currently being rendered as a
        row in the list
        """
        item["replace"]["Title"] = get_link(item["url"], item["Title"])

        # Usage
        capacity = obj.get_samples_capacity()
        samples = obj.get_samples_utilization()
        usage = capacity and samples*100/capacity or 0
        item["replace"]["Usage"] = self.get_usage_bar_html(usage)
        item["replace"]["Capacity"] = "{:01d}".format(capacity)
        item["replace"]["Samples"] = "{:01d}".format(samples)
        return item
