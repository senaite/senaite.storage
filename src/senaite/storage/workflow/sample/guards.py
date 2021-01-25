# -*- coding: utf-8 -*-

from AccessControl.SecurityInfo import ModuleSecurityInfo

security = ModuleSecurityInfo(__name__)


@security.public
def guard_store_sample(sample):
    """Sample guard to control if the sample can be stored
    """
    return True


@security.public
def guard_book_out_sample(sample):
    """Sample guard to control if the sample can be booked out
    """
    return True


@security.public
def guard_recover_sample(sample):
    """Sample guard to control if the sample can be recovered
    """
    return True
