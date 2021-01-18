# -*- coding: utf-8 -*-

import collections

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_link
from bika.lims.utils import get_link_for
from senaite.app.listing.view import ListingView
from senaite.storage.interfaces import IStoragePosition
from senaite.storage.interfaces import IStorageContainer
from plone.memoize import view


class FacilityListingView(ListingView):
    """Listing view for a storage facility
    """

    def __init__(self, context, request):
        super(FacilityListingView, self).__init__(context, request)

        self.catalog = "portal_catalog"

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

        self.title = context.Title()
        self.description = self.context.Description()
        self.form_id = "facility_listing"
        self.show_select_column = True
        self.icon_path = "{}/senaite_theme/icon/".format(self.portal_url)
        self.icon = "{}/storage-facility".format(self.icon_path)

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
            ("Description", {
                "title": _("Description")}),
            ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Collapsed"),
                "contentFilter": {"is_active": True},
                "listing_config": {
                    "selected_uids": [],
                    "expanded_rows": [],
                },
                "columns": self.columns.keys(),
            }, {
                "id": "expand",
                "title": _("Expanded"),
                "contentFilter": {
                    "sort_on": "path",
                    "review_state": "active",
                    "path": {
                        "query": api.get_path(self.context),
                    },
                },
                "listing_config": {
                    "selected_uids": [],
                    "expanded_rows": [],
                },
                "columns": self.columns.keys(),
            }
        ]

    @view.memoize
    def is_expanded(self):
        return self.review_state.get("id") == "expand"

    def folderitems(self):
        items = super(FacilityListingView, self).folderitems()
        if self.is_expanded():
            self.expand_all_children = True
        return items

    def folderitem(self, obj, item, index):
        """Applies new properties to item (StorageContainer) that is currently
        being rendered as a row in the list
        """
        item = super(FacilityListingView, self).folderitem(obj, item, index)
        obj = api.get_object(obj)
        url = api.get_url(obj)
        icon = api.get_icon(obj)
        level = self.get_child_level(obj)
        link = get_link_for(obj)
        child_uids = []

        item["replace"]["Title"] = "{} {}".format(icon, link)
        item["node_level"] = level

        # Storage position items
        if IStoragePosition.providedBy(obj):
            pid = obj.get_position_id()
            item["Id"] = pid
            item["replace"]["Id"] = get_link(url, pid)
            # append child UIDs for this object
            child_uids = self.get_child_uids_for(
                obj, types=["StorageContainer", "StoragePosition"])
            item["children"] = child_uids

        # Storage container items
        elif IStorageContainer.providedBy(obj):
            # append child UIDs
            child_uids = self.get_child_uids_for(
                obj, types=["StorageContainer", "StorageSamplesContainer"])
            item["children"] = child_uids

        return item

    def get_child_uids_for(self, obj, types=None):
        """get the child UIDs for the given object
        """
        if self.is_expanded():
            return []
        query = {
            "sort_on": "getObjPositionInParent",
            "path": {
                "query": api.get_path(obj),
                "depth": 1,
            }
        }
        if types:
            query["portal_types"] = types
        catalog = api.get_tool("portal_catalog")
        return map(api.get_uid, catalog(query))

    def get_child_level(self, obj):
        level = 0
        parent = api.get_parent(obj)
        while parent != self.context:
            level += 1
            parent = api.get_parent(parent)
        return level
