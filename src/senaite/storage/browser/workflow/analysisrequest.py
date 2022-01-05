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

from bika.lims import api
from bika.lims.browser.workflow import RequestContextAware
from bika.lims.interfaces import IWorkflowActionUIDsAdapter
from zope.interface import implementer


@implementer(IWorkflowActionUIDsAdapter)
class WorkflowActionStoreAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'store' action
    """

    def __call__(self, action, uids):
        """Redirects the user to the Storage container selector view
        """
        url = "{}/storage_store_samples?uids={}".format(
            api.get_url(self.context), ",".join(uids))
        return self.redirect(redirect_url=url)
