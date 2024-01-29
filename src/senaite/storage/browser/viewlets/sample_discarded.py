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

from bika.lims import api
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.api import dtime


class SampleDiscardedViewlet(ViewletBase):
    """Print a viewlet showing the WF history comment from a discarded sample
    """

    index = ViewPageTemplateFile("templates/sample_discarded_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        super(SampleDiscardedViewlet, self).__init__(
            context, request, view, manager=manager)
        self.context = context
        self.request = request
        self.view = view

    def is_discarded(self):
        """Returns whether the current sample is discarded
        """
        return api.get_review_status(self.context) == "discarded"

    def get_state_info(self):
        """Returns the WF state information
        """
        history = api.get_review_history(self.context)
        entry = len(history) and history[0] or {}
        actor = entry.get("actor")
        props = api.get_user_properties(actor) or {}
        date = entry.get("time")
        comments = entry.get("comments", "")
        comments = api.safe_unicode(comments)
        comments = comments.split("\r\n")
        return {
            "actor": props.get("fullname", actor),
            "date": dtime.to_localized_time(date, long_format=True),
            "comments": comments,
        }
