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
from senaite.storage.workflow.guards import GuardsAdapter


class SampleGuardsAdapter(GuardsAdapter):
    """Guards adapter for Sample content type
    """

    def guard_discard(self, sample):
        """Returns True if the sample does not have analyses assigned and does
        not have non-rejected partitions
        """
        # cannot discard samples with requested analyses
        if sample.getAnalyses(full_objects=False):
            return False

        # all partitions have to be discarded
        for uid in sample.getDescendantsUIDs():
            part = api.get_object_by_uid(uid)
            if api.get_review_status(part) != "discarded":
                return False

        return True
