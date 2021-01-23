# -*- coding: utf-8 -*-

from AccessControl.SecurityInfo import ModuleSecurityInfo
from bika.lims import api
from senaite.storage.interfaces import IStorageContainer
from senaite.storage.interfaces import IStoragePosition
from senaite.storage.interfaces import IStorageSamplesContainer

security = ModuleSecurityInfo(__name__)


@security.public
def guard_move_container(container):
    """Guard for move container
    """
    if not api.is_active(container):
        return False
    if IStoragePosition.providedBy(container):
        return True
    if IStorageContainer.providedBy(container):
        return True
    if IStorageSamplesContainer.providedBy(container):
        return True
    return False
