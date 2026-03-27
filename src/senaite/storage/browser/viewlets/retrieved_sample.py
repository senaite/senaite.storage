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
# Copyright 2019-2026 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.browser import ulocalized_time
from plone.app.layout.viewlets import ViewletBase
from plone.memoize import view


class RetrievedSampleViewlet(ViewletBase):
    """Viewlet that displays the reason why a sample was retrieved from
    storage, along with the datetime and actor
    """

    @view.memoize
    def get_recovery_transition(self):
        """Returns the most recent 'recover' action from review history
        """
        for action in api.get_review_history(self.context):
            if action.get("action") == "recover":
                return action
        return None

    def get_recovery_date(self):
        transition = self.get_recovery_transition()
        action_time = transition.get("time")
        return ulocalized_time(
            action_time, long_format=True,
            context=self.context, request=self.request)

    def get_recovered_by(self):
        transition = self.get_recovery_transition()
        return transition.get("actor")

    def get_retrieve_reason(self):
        return self.context.getRetrieveReason()

    def is_visible(self):
        """Returns whether this viewlet has to be visible
        """
        if not self.get_retrieve_reason():
            return False
        if not self.get_recovery_transition():
            return False
        return True
