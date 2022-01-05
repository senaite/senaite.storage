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
from bika.lims.utils import get_link
from bika.lims.utils import get_link_for
from bika.lims.utils import get_progress_bar_html
from senaite.app.listing import ListingView
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.interfaces import IStorageUtilization


class StorageListing(ListingView):
    """Listing view of storage-like objects
    """

    def __init__(self, context, request):
        super(StorageListing, self).__init__(context, request)

        self.catalog = STORAGE_CATALOG

        self.title = api.get_title(context)
        self.description = api.get_description(context)

        self.show_select_all_checkboxes = True
        self.show_select_column = True

        self.icon_path = "{}/senaite_theme/icon/".format(self.portal_url)

        # Context Actions
        self.context_actions = collections.OrderedDict()

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
            ("Containers", {
                "title": _("Containers")}),
        ))

    def before_render(self):
        super(StorageListing, self).before_render()
        # disable column sorting when expaned
        if self.is_expanded():
            self.toggle_column_sorting(False)

    def is_expanded(self):
        return self.review_state.get("id") == "expand"

    def toggle_column_sorting(self, toggle=False):
        """Toggle column sorting on/off
        """
        for key, value in self.columns.items():
            value["sortable"] = toggle

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
        item = super(StorageListing, self).folderitem(obj, item, index)

        obj = api.get_object(obj)
        icon = api.get_icon(obj)
        level = self.get_child_level(obj)
        link = get_link_for(obj)

        item["replace"]["Title"] = "{} {}".format(icon, link)
        item["Description"] = api.get_description(obj)
        item["replace"]["Id"] = get_link(item["url"], api.get_id(obj))
        item["node_level"] = level

        # Samples usage
        utilization = IStorageUtilization(obj)
        capacity = utilization.get_samples_capacity()
        samples = utilization.get_samples_utilization()
        percentage = capacity and samples*100/capacity or 0
        item["replace"]["SamplesUsage"] = self.get_usage_bar_html(percentage)
        item["replace"]["Samples"] = "{:01d} / {:01d} ({:01d}%)"\
            .format(samples, capacity, percentage)

        if self.is_expanded() and level == 0:
            item["state_class"] = "table-primary"
        elif self.is_expanded() and level > 0:
            item["state_class"] = "table-light"

        return item

    def get_child_level(self, obj):
        if obj == self.context:
            return 0
        level = 0
        parent = api.get_parent(obj)
        while parent != self.context:
            level += 1
            parent = api.get_parent(parent)
        return level
