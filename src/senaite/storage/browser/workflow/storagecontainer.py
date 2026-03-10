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
from bika.lims.browser.workflow import RequestContextAware
from bika.lims.browser.workflow import WorkflowActionGenericAdapter
from bika.lims.interfaces import IWorkflowActionUIDsAdapter
from senaite.storage import api as sapi
from senaite.storage.interfaces import IStorageLayoutContainer
from senaite.storage.interfaces import IStorageSamplesContainer
from zope.interface import implementer


@implementer(IWorkflowActionUIDsAdapter)
class WorkflowActionRecoverSamplesAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of StorageSamplesContainer 'recover_samples' action.
    Redirects to the retrieve reasons form when reasons are configured.
    """

    def __call__(self, action, uids):
        reasons = sapi.get_retrieve_reasons()
        if reasons:
            # Collect sample UIDs from all selected containers
            sample_uids = []
            for uid in uids:
                obj = api.get_object_by_uid(uid)
                if IStorageSamplesContainer.providedBy(obj):
                    sample_uids.extend(obj.get_samples_uids())
            if sample_uids:
                url = "{}/storage_retrieve_samples?uids={}".format(
                    api.get_url(self.context), ",".join(sample_uids))
                return self.redirect(redirect_url=url)

        # No reasons configured, fall back to the generic adapter
        return super(
            WorkflowActionRecoverSamplesAdapter, self
        ).__call__(action, uids)


@implementer(IWorkflowActionUIDsAdapter)
class WorkflowActionAddSamplesAdapter(RequestContextAware):
    """Adapter in charge of "add samples" action
    """

    def __call__(self, action, uids):
        """Redirects the user to the Samples selector view
        """
        # filter out UIDs not belonging to sample containers
        objs = map(api.get_object, uids)
        containers = filter(
            lambda o: IStorageSamplesContainer.providedBy(o), objs)
        container_uids = map(api.get_uid, containers)
        url = "{}/storage_store_container?uids={}".format(
            self.back_url, ",".join(container_uids))
        return self.redirect(redirect_url=url)


@implementer(IWorkflowActionUIDsAdapter)
class WorkflowActionMoveContainerAdapter(RequestContextAware):
    """Adapter in charge of "move container" action
    """

    def __call__(self, action, uids):
        """Redirects the user to the Samples selector view
        """
        # filter out UIDs not belonging to sample containers
        objs = map(api.get_object, uids)
        containers = filter(
            lambda o: IStorageLayoutContainer.providedBy(o), objs)
        container_uids = map(api.get_uid, containers)
        url = "{}/storage_move_container?uids={}".format(
            self.back_url, ",".join(container_uids))
        return self.redirect(redirect_url=url)
