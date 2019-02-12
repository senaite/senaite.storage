# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from AccessControl.SecurityInfo import ModuleSecurityInfo
from senaite.storage.interfaces import IStorageSamplesContainer

security = ModuleSecurityInfo(__name__)

@security.public
def guard_recover_samples(samples_container):
    """ Guard for recover all samples from this container
    """
    if not IStorageSamplesContainer.providedBy(samples_container):
        return False
    return samples_container.has_samples()


@security.public
def guard_add_samples(samples_container):
    """Guard for adding samples to this container
    """
    if not IStorageSamplesContainer.providedBy(samples_container):
        return False
    return not samples_container.is_full()
