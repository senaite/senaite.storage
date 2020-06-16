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
from bika.lims.api import get_icon
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_link, get_progress_bar_html
from senaite.storage import senaiteMessageFactory as _


class StorageListing(BikaListingView):
    """Listing view of storage-like objects
    """

    def __init__(self, context, request):
        super(StorageListing, self).__init__(context, request)
        self.sort_on = "sortable_title"
        self.show_select_row = False
        self.show_select_all_checkboxes = False
        self.show_select_column = False
        self.context_actions = collections.OrderedDict()

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Name"),
                "index": "sortable_title"}),
            ("Id", {
                "title": _("ID")}),
            ("SamplesUsage", {
                "title": _("% Samples"),}),
            ("Samples", {
                "title": _("Samples"),}),
            ("Containers", {
                "title": _("Containers"),}),
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
        p_bar = get_progress_bar_html(percentage)
        return p_bar.replace('class="progress-bar',
                             'class="progress-bar {}'.format(css_class))

    def folderitem(self, obj, item, index):
        """Applies new properties to item that is currently being rendered as a
        row in the list
        """
        obj = api.get_object(obj)
        item["replace"]["Title"] = get_link(item["url"], item["Title"])
        item["replace"]["Id"] = get_link(item["url"], api.get_id(obj))

        # Samples usage
        capacity = obj.get_samples_capacity()
        samples = obj.get_samples_utilization()
        percentage = capacity and samples*100/capacity or 0
        item["replace"]["SamplesUsage"] = self.get_usage_bar_html(percentage)
        item["replace"]["Samples"] = "{:01d} / {:01d} ({:01d}%)"\
            .format(samples, capacity, percentage)

        # Container types icons
        item["before"]["Title"] = get_icon(obj)

        return item
