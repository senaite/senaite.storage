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
from senaite.storage.browser.storagelisting import StorageListing


class StorageRootFolderContentsView(StorageListing):
    """Listing view of all StorageFacilities
    """

    def __init__(self, context, request):
        super(StorageRootFolderContentsView, self).__init__(context, request)
        self.title = self.context.translate(_("Samples storage"))
        self.form_id = "list_storagerootfolder"
        self.contentFilter = dict(
            portal_type = "StorageFacility",
            sort_on = "sortable_title",
            sort_order = "ascending"
        )
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++senaite.storage.static/img/storage_big.png")

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Name"),
                "index": "sortable_index"}),
            ("SamplesUsage", {
                "title": _("Samples"),}),
            ("Samples", {
                "title": _("Samples usage"),}),
            ("Containers", {
                "title": _("Containers"),}),
            ("Phone", {
                "title": _("Phone"),}),
            ("EmailAddress", {
                "title": _("Email"),}),
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

        # Add Facility button
        self.context_actions[_("Add Facility")] = {
            "url": "createObject?type_name=StorageFacility",
            "icon": "++resource++bika.lims.images/add.png"
        }


    def folderitem(self, obj, item, index):
        """Applies new properties to item (StorageFacility) that is currently
        being rendered as a row in the list
        """
        item = super(StorageRootFolderContentsView,
                     self).folderitem(obj, item, index)

        item["replace"]["EmailAddress"] = get_email_link(item["EmailAddress"])
        phone = obj.getPhone()
        if phone:
            item["replace"]["Phone"] = get_link("tel:{}".format(phone), phone)

        # Containers
        containers = obj.get_layout_containers()
        item["replace"]["Containers"] = "{:01d}".format(len(containers))
        return item
