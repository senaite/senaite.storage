# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

import collections

from bika.lims import api
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.browser.storagelisting import StorageListing
from senaite.storage.interfaces import IStorageFacility


class ContainersView(StorageListing):
    """Listing view of all StorageContainers
    """

    def __init__(self, context, request):
        super(ContainersView, self).__init__(context, request)
        self.title = context.Title()
        self.form_id = "list_storage_containers"
        self.contentFilter = {
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": "/".join(context.getPhysicalPath()),
                "depth": 1,
            }
        }

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Name"),
                "index": "sortable_index"}),
            ("Temperature", {
                "title": _("Temperature"),}),
            ("Usage", {
                "title": _("Usage"),}),
            ("Samples", {
                "title": _("Samples"),}),
            ("Capacity", {
                "title": _("Capacity"),}),
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
        icon_name = "container_big.png"
        if IStorageFacility.providedBy(self.context):
            icon_name = "facility_big.png"
        self.icon = "{}/++resource++senaite.storage.static/img/{}"\
            .format(self.portal_url, icon_name)

        self.context_actions[_("Add")] = {
            "url": "createObject?type_name=StorageContainer",
            "icon": "++resource++bika.lims.images/add.png"
        }


    def folderitem(self, obj, item, index):
        """Applies new properties to item (StorageContainer) that is currently
        being rendered as a row in the list
        """
        item = super(ContainersView, self).folderitem(obj, item, index)

        # Containers
        containers = obj.get_layout_containers()
        item["replace"]["Containers"] = "{:01d}".format(len(containers))

        # append the UID of the primary AR as parent
        parent = api.get_uid(api.get_parent(obj))
        item["parent"] = parent != api.get_uid(self.context) and parent or ""
        # append partition UIDs of this AR as children
        item["children"] = map(lambda cont: api.get_uid(cont), containers)
        return item
