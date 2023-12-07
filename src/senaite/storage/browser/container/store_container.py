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

import json

from bika.lims import api
from bika.lims import bikaMessageFactory as _s
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.workflow import SAMPLE_WORKFLOW
from senaite.storage import logger
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.browser import BaseView
from senaite.storage.interfaces import IStorageSamplesContainer
from senaite.core.catalog import SAMPLE_CATALOG

DISPLAY_TEMPLATE = "<a href='${url}' _target='blank'>${getId}</a>"


class StoreContainerView(BaseView):
    """Store Container View.

    Allows to store samples in preselected containers.

    View displayed when coming from the storage container listing.
    """
    template = ViewPageTemplateFile("templates/store_container.pt")

    def __init__(self, context, request):
        super(StoreContainerView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.back_url = self.context.absolute_url()
        self.container = None

    def get_container(self):
        """Returns the current samples container based on the uids passed in the
        request
        """
        if self.container:
            return self.container
        request_uids = self.get_uids_from_request()
        if not request_uids:
            if IStorageSamplesContainer.providedBy(self.context):
                self.container = self.context
        else:
            self.container = api.get_object_by_uid(request_uids[0])
        return self.container

    def get_fallback_url(self):
        """Returns the fallback url with the current container selected
        """
        current_uid = api.get_uid(self.get_container())
        request_uids = self.get_uids_from_request() or []
        request_uids.insert(0, current_uid)
        request_uids = list(set(request_uids))
        request_uids = ",".join(request_uids)
        return "{}/{}?uids={}".format(
            self.back_url, self.__name__, request_uids)

    def get_next_url(self):
        """Returns the next url the system has to redirect to after submit. If
        multiple containers were specified in the request (uids), this function
        will return the url with the next uids to be processed. It fallbacks to
        back_url otherwise
        """
        next_uids = self.get_next_uids()
        if next_uids:
            next_uids = ",".join(next_uids)
            return "{}/{}?uids={}".format(
                self.back_url, self.action, next_uids)
        return self.back_url

    def get_next_container(self):
        """Returns the next container from the list of uids from the request
        that have not been yet processed or None
        """
        next_uids = self.get_next_uids()
        if next_uids:
            container = api.get_object_by_uid(next_uids[0])
            if IStorageSamplesContainer.providedBy(container):
                return container
        return None

    def get_next_uids(self):
        """Return the list of uids from the request that have not been processed
        """
        current_uid = api.get_uid(self.get_container())
        request_uids = self.get_uids_from_request()
        return filter(lambda uid: uid != current_uid, request_uids)

    def is_last_container(self):
        """Returns whether the view is processing the last container from the
        list of container uids passed in through the request
        """
        if self.get_next_uids():
            return False
        return True

    def get_base_query(self):
        base_query = {
            "review_state": self.get_allowed_states(),
            "sort_on": "created"
        }
        return json.dumps(base_query)

    def get_sample_info(self, sample):
        """Returns the sample info
        """
        if not sample:
            return {}
        sample = api.get_object(sample)
        wf_tool = api.get_tool("portal_workflow")
        sample_wf = wf_tool[SAMPLE_WORKFLOW]
        status = api.get_workflow_status_of(sample)
        status_title = status
        state = sample_wf.states.get(status)
        if state:
            status_title = state.title
        return {
            "obj": sample,
            "id": api.get_id(sample),
            "uid": api.get_uid(sample),
            "title": api.get_title(sample),
            "url": api.get_url(sample),
            "sample_type": sample.getSampleTypeTitle(),
            "status": status,
            "status_title": status_title,
        }

    def get_allowed_states(self):
        # Get the Sample (aka AR) workflow definition
        portal_wf = api.get_tool("portal_workflow")
        arwf = portal_wf[SAMPLE_WORKFLOW]
        ar_states = arwf.states

        allowed_states = []

        # Get the states for which transition "store" is possible
        for state in ar_states:

            if "store" in ar_states._mapping.get(state).transitions:
                allowed_states.append(state)

        return allowed_states

    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)
        form_store = form.get("button_store", False)
        form_cancel = form.get("button_cancel", False)

        # Get the container
        container = self.get_container()
        if not container:
            return self.redirect(message=_s("No items selected"),
                                 level="warning")
        if not IStorageSamplesContainer.providedBy(container):
            logger.warn("Not a samples container: {}".format(repr(container)))
            return self.redirect(redirect_url=self.get_next_url())

        # If container is full, there is no way to add more samples there
        if container.is_full():
            message = _("Cannot store samples. Samples container {} is full")
            return self.redirect(message=message.format(api.get_id(container)),
                                 level="warning")

        # Handle store
        if form_submitted and form_store:
            alpha_position = form.get("position")
            sample_uid = form.get("sample")
            if not alpha_position or not api.is_uid(sample_uid):
                message = _("No position or not valid sample selected")
                return self.redirect(message=message)

            sample = api.get_object(sample_uid)
            logger.info("Storing sample {} in {} at {}".format(
                api.get_id(sample), api.get_id(container), alpha_position))

            # Store
            position = container.alpha_to_position(alpha_position)
            if container.add_object_at(sample, position[0], position[1]):
                message = _("Stored sample {} at position {}").format(
                    api.get_id(sample), alpha_position)
                if container.is_full():
                    return self.redirect(redirect_url=self.get_next_url())
                return self.redirect(redirect_url=self.get_fallback_url(),
                                     message=message)

        # Handle cancel
        if form_submitted and form_cancel:
            return self.redirect(message=_("Sample storing canceled"))

        return self.template()

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
                "portal_type": ["AnalysisRequest"],
                "review_state": [
                    "received",
                    "to_be_verified",
                    "verified",
                    "published",
                ],
                "sort_on": "sortable_title",
                "sort_order": "ascending",
            },
            "data-catalog": SAMPLE_CATALOG,
            "data-search_index": "listing_searchable_text",
            "data-search_wildcard": True,
            "data-allow_user_value": False,
            "data-columns": [{
                "name": "getId",
                "label": _("Sample ID"),
                "width": "15",
            }, {
                "name": "getClientSampleID",
                "label": _("CSID"),
                "width": "15",
            }, {
                "name": "getClientID",
                "label": _("Client ID"),
                "width": "35",
            }, {
                "name": "getSampleTypeTitle",
                "label": _("Sample Type"),
                "width": "25",
            }, {
                "name": "review_state",
                "label": _("State"),
                "width": "10",
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
