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
from bika.lims.utils import changeWorkflowState
from bika.lims.workflow import doActionFor as do_action_for
from senaite.core.workflow import SAMPLE_WORKFLOW
from senaite.storage import api as _api
from senaite.storage.api import pause_snapshots_for
from senaite.storage.api import resume_snapshots_for


def after_store(sample):
    """Event triggered after "store" transition takes place for a given sample
    """
    primary = sample.getParentAnalysisRequest()
    if not primary:
        return

    # Store primary sample if its partitions have been stored
    parts = primary.getDescendants()

    # Partitions in some statuses won't be considered
    skip = ["cancelled", "stored", "retracted", "rejected"]
    parts = filter(lambda part: api.get_review_status(part) not in skip, parts)
    if not parts:
        # There are no partitions left, transition the primary
        do_action_for(primary, "store")


def after_book_out(sample):
    """Event triggered after "book_out" transition takes place for a given sample
    """

    # remove the sample from the container
    _api.remove_sample_from_container(sample)

    primary = sample.getParentAnalysisRequest()
    if not primary:
        return

    # Store primary sample if its partitions have been stored
    parts = primary.getDescendants()

    # Partitions in some statuses won't be considered
    skip = ["cancelled", "stored", "retracted", "rejected"]
    parts = filter(lambda part: api.get_review_status(part) not in skip, parts)
    if not parts:
        # There are no partitions left, transition the primary
        do_action_for(primary, "book_out")


def after_recover(sample):
    """Unassigns the sample from its storage container and "recover". It also
    transitions the sample to its previous state before it was stored
    """
    # remove the sample from the container
    _api.remove_sample_from_container(sample)
    # Transition the sample to the state before it was stored
    previous_state = _api.get_previous_state(sample, default="sample_due")
    # Note: we pause the snapshots here because events are fired next
    pause_snapshots_for(sample)
    changeWorkflowState(sample, SAMPLE_WORKFLOW, previous_state)
    resume_snapshots_for(sample)

    # Reindex the sample
    sample.reindexObject()

    # If the sample is a partition, try to promote to the primary
    primary = sample.getParentAnalysisRequest()
    if not primary:
        return

    # Recover primary sample if all its partitions have been recovered
    parts = primary.getDescendants()

    # Partitions in some statuses won't be considered.
    skip = ["stored", "booked_out"]
    parts = filter(lambda part: api.get_review_status(part) in skip, parts)
    if not parts:
        # There are no partitions left, transition the primary
        do_action_for(primary, "recover")
