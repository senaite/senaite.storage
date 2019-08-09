# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE.
#
# SENAITE.CORE.LISTING is free software: you can redistribute it and/or modify
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
# Copyright 2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.utils import changeWorkflowState
from bika.lims.workflow import getReviewHistory
from senaite.storage import api as _api
from senaite.storage import logger


def after_recover(sample):
    """Unassigns the sample from its storage container and "recover". It also
    transitions the sample to its previous state before it was stored
    """
    container = _api.get_storage_sample(api.get_uid(sample))
    if container:
        container.remove_object(sample)
    else:
        logger.warn("Container for Sample {} not found".format(sample.getId()))

    # Transition the sample to the state before it was stored
    previous_state = get_previous_state(sample, "stored") or "sample_received"
    changeWorkflowState(sample, "bika_ar_workflow", previous_state)


def get_previous_state(instance, state):
    history = getReviewHistory(instance, reverse=True)
    history = map(lambda event: event["review_state"], history)
    for status in history:
        if status != state:
            return status
    return None
