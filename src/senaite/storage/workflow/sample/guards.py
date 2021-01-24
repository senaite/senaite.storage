# -*- coding: utf-8 -*-

from AccessControl.SecurityInfo import ModuleSecurityInfo
from bika.lims import api

security = ModuleSecurityInfo(__name__)


@security.public
def guard_store_sample(sample):
    """Sample guard to control if the sample can be stored

    Only possible when all analyses are readonly
    """
    return not has_editable_analyses(sample)


@security.public
def guard_book_out_sample(sample):
    """Sample guard to control if the sample can be booked out

    Only possible when all analyses are readonly
    """
    return not has_editable_analyses(sample)


@security.public
def guard_recover_sample(sample):
    """Sample guard to control if the sample can be recovered
    """
    return True


def has_editable_analyses(sample):
    """Checks if the sample contains editable analyses

    This ensures there are no analyses where fields are editable.
    """
    analyses = sample.getAnalyses()
    if not analyses:
        return False
    for analysis in analyses:
        status = api.get_workflow_status_of(analysis)
        if status in ["assigned", "unassigned"]:
            return True
    return False
