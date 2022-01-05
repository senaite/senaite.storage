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
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.storage import logger
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.api import get_parents
from senaite.storage.browser import BaseView
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.interfaces import IStorageContainer
from senaite.storage.interfaces import IStorageFacility
from senaite.storage.interfaces import IStorageSamplesContainer


class MoveContainerView(BaseView):
    """Allows to move containers in other facilities/positions/containers
    """
    template = ViewPageTemplateFile("templates/move_container.pt")

    def __init__(self, context, request):
        super(MoveContainerView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.portal = api.get_portal()
        self.back_url = "{}/senaite_storage".format(api.get_url(self.portal))

    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)
        form_move = form.get("button_move", False)
        form_cancel = form.get("button_cancel", False)

        # No items selected
        if not self.get_objects():
            return self.redirect(
                message=_("No items selected"), level="warning")

        # Handle store
        if form_submitted and form_move:
            logger.info("*** MOVE CONTAINER ***")
            move = form.get("move", {})
            for src, dest in move.items():
                self.move_container(src, dest)
            return self.redirect()

        # Handle cancel
        if form_submitted and form_cancel:
            return self.redirect(message=_("Container moving cancelled"))

        return self.template()

    def get_objects(self):
        """Get the objects to be moved
        """
        # fetch objects from request
        objs = self.get_objects_from_request()
        if objs:
            return objs
        if IStorageSamplesContainer.providedBy(self.context):
            return [self.context]
        if IStorageContainer.providedBy(self.context):
            return [self.context]
        return []

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def move_container(self, src, dest):
        """move container from source to destination
        """
        source = api.get_object(src)
        destination = api.get_object(dest)
        parent = api.get_parent(source)

        if destination == parent:
            message = _(u"Container {} is already located in destination path!"
                        .format(self.get_container_path(source)))
            self.add_status_message(message, level="warning")
            return False
        cb = parent.manage_cutObjects(ids=[api.get_id(source)])
        destination.manage_pasteObjects(cb_copy_data=cb)

        message = _(u"Moved container {} → {}".format(
            self.get_title(source), self.get_container_path(destination)))
        self.add_status_message(message, level="info")
        return True

    def get_parents_for(self, container):
        """Get the parent objects for the container
        """
        if IStorageFacility.providedBy(container):
            return [container]

        def predicate(obj):
            return IStorageFacility.providedBy(obj)

        return get_parents(container, predicate=predicate)

    def get_title(self, obj):
        """Return the object title as unicode
        """
        title = api.get_title(obj)
        return api.safe_unicode(title)

    def get_container_path(self, container):
        """Return the facility container path
        """
        parents = list(reversed(self.get_parents_for(container)))
        parents.append(container)
        return " / ".join(map(self.get_title, parents))

    def get_movable_containers(self):
        """Get movable containers

        NOTE: contained containers will be omitted
        """
        movable_containers = []
        containers = self.get_objects()
        for container in containers:
            parents = self.get_parents_for(container)
            if set(parents).intersection(containers):
                continue
            movable_containers.append(container)
        return movable_containers

    def get_move_targets_for(self, container):
        """Get move targets for the given container
        """
        targets = []
        container_path = api.get_path(container)
        target_types = [
            "StorageFacility",
            "StoragePosition",
            "StorageContainer",
        ]
        # sample containers can only be moved inside containers
        if IStorageSamplesContainer.providedBy(container):
            target_types = ["StorageContainer"]
        query = {
            "portal_type": target_types,
            "review_state": "active"
        }
        brains = api.search(query, STORAGE_CATALOG)
        for brain in brains:
            path = api.get_path(brain)
            if path.startswith(container_path):
                continue
            targets.append(api.get_object(brain))
        return targets

    def get_container_data(self):
        """Returns a list of containers that can be moved

        """
        for obj in self.get_movable_containers():
            obj = api.get_object(obj)
            yield {
                "obj": obj,
                "id": api.get_id(obj),
                "uid": api.get_uid(obj),
                "title": self.get_title(obj),
                "path": self.get_container_path(obj),
                "url": api.get_url(obj),
                "targets": self.get_move_targets_for(obj),
            }
