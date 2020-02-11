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
from senaite.storage import logger
from senaite.storage.interfaces import IStorageLayoutContainer


def StorageContentModifiedEventHandler(container, event):
    """Adds the object to the parent's layout (if the parent is a container)
    We use a ObjectModifiedEvent from zope.lifecycleevent here instead of
    ObjectAddedEvent or InitializedEvent because:

    a) ObjectAddedEvent from zope.lifecycleevent is fired as soon as the object
       is temporarily created, when fields do not have any value set. Since we
       need the values from "PositionsLayout" field for the parent to get
       updated in accordance, we cannot use this event.

    b) InitializedEvent from Products.Archetypes is called as soon as the object
       is created (with values) after the edit form submission, but this event
       is not called by senaite.core's api. Hence, this cannot be used because
       the event will not be fired if the object is created manually unless we
       do a explicit call to processForm() on creation (which is not always the
       case).

    Caveats: Note that we assume the object is at least created by using Plone's
    default edit form or by using senaite.core's api, but if the object is
    created manually (e.g. using _createObjectByType), this event will not be
    fired.
    """
    parent = api.get_parent(container)
    if not IStorageLayoutContainer.providedBy(parent):
        # Parent doesn't care about the changes in his children
        return

    if parent.has_object(container):
        if not parent.update_object(container):
            logger.warn("Cannot update the container '{}' from '{}'"
                        .format(container.getId(), parent.getId()))

    else:
        # The object is added at the first available position, if any
        if not parent.add_object(container):
            logger.warn("Cannot add the container '{}' into '{}'"
                        .format(container.getId(), parent.getId()))


def StorageContentRemovedEventHandler(container, event):
    """Removes the object from parent's layout (if the parent is a container)
    """
    parent = api.get_parent(container)
    if not IStorageLayoutContainer.providedBy(parent):
        return

    if not parent.remove_object(container):
        logger.warn("Cannot remove the container '{}' from '{}'"
                    .format(container.getId(), parent.getId()))

