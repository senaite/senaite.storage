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
# Copyright 2019-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections
import json

from bika.lims import api
from Products.Five.browser import BrowserView
from senaite.storage import logger
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.catalog import STORAGE_CATALOG

DISPLAY_TEMPLATE = "<a href='${url}' _target='blank'>${get_full_title}</a>"


class BaseView(BrowserView):
    """Vitaminized Browser View
    """

    def get_objects_from_request(self):
        """Returns a list of objects coming from the "uids" request parameter
        """
        unique_uids = self.get_uids_from_request()
        return filter(None, map(self.get_object_by_uid, unique_uids))

    def get_uids_from_request(self):
        """Return a list of uids from the request
        """
        uids = self.request.form.get("uids", "")
        if isinstance(uids, basestring):
            uids = uids.split(",")
        unique_uids = collections.OrderedDict().fromkeys(uids).keys()
        return filter(api.is_uid, unique_uids)

    def get_object_by_uid(self, uid):
        """Get the object by UID
        """
        logger.debug("get_object_by_uid::UID={}".format(uid))
        obj = api.get_object_by_uid(uid, None)
        if obj is None:
            logger.warn("!! No object found for UID #{} !!")
        return obj

    def redirect(self, redirect_url=None, message=None, level="info"):
        """Redirect with a message
        """
        if redirect_url is None:
            redirect_url = self.back_url
        if message is not None:
            self.add_status_message(message, level)
        return self.request.response.redirect(redirect_url)

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def get_reference_widget_attributes(self, name, obj):
        """Return input widget attributes for the ReactJS component
        """
        url = api.get_url(obj)

        attributes = {
            "data-name": name,
            "data-values": [],
            "data-records": {},
            "data-value_key": "uid",
            "data-value_query_index": "UID",
            "data-api_url": "%s/referencewidget_search" % url,
            "data-query": {
                "portal_type": ["StorageSamplesContainer"],
                "is_full": False,
                "review_state": "active",
                "sort_on": "getId",
                "sort_order": "ascending",
            },
            "data-catalog": STORAGE_CATALOG,
            "data-search_index": "listing_searchable_text",
            "data-search_wildcard": True,
            "data-allow_user_value": False,
            "data-columns": [{
                "name": "id",
                "label": _("Id"),
                "width": 10,
            }, {
                "name": "get_full_title",
                "label": _("Container path"),
                "width": 90,
            }],
            "data-display_template": DISPLAY_TEMPLATE,
            "data-limit": 5,
            "data-multi_valued": False,
            "data-disabled": False,
            "data-readonly": False,
            "data-required": False,
            "data-clear_results_after_select": False,
        }

        for key, value in attributes.items():
            # convert all attributes to JSON
            attributes[key] = json.dumps(value)

        return attributes
