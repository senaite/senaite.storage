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
# Copyright 2019-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.storage import logger
from senaite.storage import senaiteMessageFactory as _s
from senaite.storage.browser import BaseView
from senaite.storage.catalog import STORAGE_CATALOG

DISPLAY_TEMPLATE = "<a href='${url}' _target='blank'>${get_full_title}</a>"


class StoreSamplesView(BaseView):
    """Store Samples view.

    Allows to store preselected samples to containers.

    View displayed when coming from the samples listing.
    """
    template = ViewPageTemplateFile("templates/store_samples.pt")

    def __init__(self, context, request):
        super(StoreSamplesView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.back_url = self.context.absolute_url()

    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)
        form_store = form.get("button_store", False)
        form_cancel = form.get("button_cancel", False)

        samples = self.get_objects_from_request()
        stored_samples = []

        # No items selected
        if not samples:
            return self.redirect(message=_("No items selected"),
                                 level="warning")

        # Handle store
        if form_submitted and form_store:

            # extract relevant data
            container_mapping = form.get("sample_container", {})
            container_position_mapping = form.get("sample_container_position", {})

            for sample in samples:
                sample_uid = api.get_uid(sample)
                container_uid = container_mapping.get(sample_uid)
                alpha_position = container_position_mapping.get(sample_uid)
                if not all([container_uid, alpha_position]):
                    continue
                sample_obj = self.get_object_by_uid(sample_uid)
                container = self.get_object_by_uid(container_uid)
                logger.info("Storing sample {} in {}"
                            .format(sample.getId(), container.getId()))
                # Store
                position = container.alpha_to_position(alpha_position)
                stored = container.add_object_at(sample_obj, position[0],
                                                 position[1])
                if stored:
                    stored = container.get_object_at(position[0], position[1])
                    stored_samples.append(stored)

            message = _s("Stored {} samples: {}".format(
                len(stored_samples), ", ".join(
                    map(api.get_title, stored_samples))))

            return self.redirect(message=message)

        # Handle cancel
        if form_submitted and form_cancel:
            return self.redirect(message=_s("Sample storing canceled"))

        return self.template()

    def get_samples_data(self):
        """Returns a list of AR data
        """
        for obj in self.get_objects_from_request():
            obj = api.get_object(obj)
            yield {
                "obj": obj,
                "id": api.get_id(obj),
                "uid": api.get_uid(obj),
                "title": api.get_title(obj),
                "path": api.get_path(obj),
                "url": api.get_url(obj),
                "sample_type": api.get_title(obj.getSampleType())
            }

    def get_reference_widget_attributes(self, name, obj=None):
        """Return input widget attributes for the ReactJS component
        """
        if obj is None:
            obj = self.context
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
