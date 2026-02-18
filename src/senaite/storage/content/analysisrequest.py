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
# Copyright 2019-2026 by it's authors.
# Some rights reserved, see README and LICENSE.

from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from bika.lims.interfaces import IAnalysisRequest
from senaite.core.browser.widgets import DateTimeWidget
from senaite.storage.archetypes.field import ExtDateTimeField
from senaite.storage.interfaces import ISenaiteStorageLayer
from zope.component import adapter
from zope.interface import implementer


fields = [
    ExtDateTimeField(
        "StorageExpiryDate",
        default=None,
        widget=DateTimeWidget(
            visible=False,
        ),
    ),
]


@adapter(IAnalysisRequest)
@implementer(ISchemaExtender, IBrowserLayerAwareExtender)
class AnalysisRequestSchemaExtender(object):
    """Extends AnalysisRequest schema with storage-specific fields
    """

    layer = ISenaiteStorageLayer

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return fields
