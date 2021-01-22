# -*- coding: utf-8 -*-

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
