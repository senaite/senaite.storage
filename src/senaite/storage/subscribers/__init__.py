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
from senaite.storage import logger
from senaite.storage.interfaces import IStorageLayoutContainer


def update_parent_layout(container):
    """Adds the container to the layout of its parent, or updates it there

    The parent keeps the capacity and utilization of the container in its
    own layout, so it has to learn about the container when it is added and
    whenever its dimensions change. Does nothing when the parent is not a
    layout container itself, e.g. a storage facility.
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


def StorageContentAddedEventHandler(container, event):
    """Event handler when a new layout container was added

    The add form sets the fields before the container is added, so its
    layout is complete here and the parent can take it in.
    """
    container.rebuild_layout()
    update_parent_layout(container)


def StorageContentCreatedByAPIEventHandler(container, event):
    """Event handler when a layout container was created with `api.create`

    `api.create` adds the container before it sets its fields, and sets
    them through the fields rather than the setters, so neither the layout
    of the container nor the one of its parent know its dimensions yet.
    """
    container.rebuild_layout()
    update_parent_layout(container)


def StorageContentModifiedEventHandler(container, event):
    """Rebuilds the layout when the dimensions of the container changed, and
    adds the container to the layout of its parent, or updates it there

    A container the parent did not take in when it was added, e.g. because
    it had no free position then, is added here on its next modification.
    """
    modified = [d.attributes[0] for d in event.descriptions if d.attributes]
    if "rows" in modified or "columns" in modified:
        container.rebuild_layout()

    update_parent_layout(container)


def StorageContentRemovedEventHandler(container, event):
    """Removes the object from parent's layout (if the parent is a container)
    """
    parent = api.get_parent(container)
    if not IStorageLayoutContainer.providedBy(parent):
        return

    if not parent.remove_object(container):
        logger.warn("Cannot remove the container '{}' from '{}'"
                    .format(container.getId(), parent.getId()))

