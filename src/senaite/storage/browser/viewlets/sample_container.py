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

from bika.lims import api
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.storage.catalog import SENAITE_STORAGE_CATALOG
from bika.lims import workflow as wf


class SampleContainerViewlet(ViewletBase):
    """Print a viewlet showing the container where current sample is stored
    """
    template = ViewPageTemplateFile("templates/sample_container_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        super(SampleContainerViewlet, self).__init__(
            context, request, view, manager=manager)
        self.context = context
        self.request = request
        self.view = view

    def is_stored(self):
        """Returns whether the current sample is stored
        """
        return api.get_review_status(self.context) == "stored"

    def get_sample_container_info(self):
        """Returns the storage container this Sample is stored in
        """
        # Search the container the sample is stored in
        query = {"portal_type": "StorageSamplesContainer",
                 "get_samples_uids": api.get_uid(self.context)}
        brains = api.search(query, SENAITE_STORAGE_CATALOG)
        if not brains:
            return None

        # Get the data info from the container
        container = api.get_object(brains[0])
        position = container.get_object_position(self.context)
        position = container.position_to_alpha(position[0], position[1])
        return {
            "uid": api.get_uid(container),
            "id": api.get_id(container),
            "title": api.get_title(container),
            "url": api.get_url(container),
            "position": position,
            "full_title": container.get_full_title(),
            "when": wf.getTransitionDate(self.context, "store"),
        }

    def index(self):
        if self.is_stored():
            return ""
        return self.template()
