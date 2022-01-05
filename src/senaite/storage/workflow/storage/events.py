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
from senaite.storage import logger
from senaite.storage.api import get_parents
from senaite.storage.interfaces import IStorageRootFolder

PROGRESS_FLAG = "_v_progress"


def after_activate(obj):
    """Event triggered after "activate" transition
    """

    def activate_children(children):
        for child in children:
            if api.is_active(child):
                continue
            logger.info("*** Activating {} ***".format(api.get_id(child)))
            api.do_transition_for(child, "activate")
            activate_children(child.objectValues())

    if not event_in_progress(obj):
        # toggle progress flag on
        toggle_in_progress(obj, True)
        # also activate all children
        activate_children(obj.objectValues())
        # toggle progress flag off
        toggle_in_progress(obj, False)


def after_deactivate(obj):
    """Event triggered after "deactivate" transition
    """

    def deactivate_children(children):
        for child in children:
            if not api.is_active(child):
                continue
            logger.info("*** Deactivating {} ***".format(api.get_id(child)))
            api.do_transition_for(child, "deactivate")
            deactivate_children(child.objectValues())

    if not event_in_progress(obj):
        # toggle progress flag on
        toggle_in_progress(obj, True)
        # deactivate all children
        deactivate_children(obj.objectValues())
        # toggle progress flag off
        toggle_in_progress(obj, False)


def toggle_in_progress(obj, toggle):
    """toggle the progress flag on the object
    """
    logger.info("Set progress flag for {} -> {}".format(repr(obj), toggle))
    setattr(obj, PROGRESS_FLAG, toggle)


def event_in_progress(obj):
    """Checks if the current object or one of the parents is in progress
    """
    if is_obj_in_progress(obj):
        return True
    parents = get_parents(
        obj, predicate=lambda o: IStorageRootFolder.providedBy(o))
    return any(map(is_obj_in_progress, parents))


def is_obj_in_progress(obj):
    """Checks the progress flag on the object
    """
    return getattr(obj, PROGRESS_FLAG, False)
