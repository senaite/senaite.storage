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

from senaite.core.interfaces import IGetStickerTemplates
from senaite.storage import senaiteMessageFactory as _
from zope.interface import implementer

# Sticker template shipped by this package. The prefix matches the resource
# directory name registered via <plone:static type="stickers">.
STORAGE_STICKER = "senaite.storage:StorageLocation_50x30mm.pt"


@implementer(IGetStickerTemplates)
class GetStorageStickers(object):
    """Sticker templates for storage location objects (facilities, positions,
    containers and samples containers)
    """
    default_template = STORAGE_STICKER

    def __init__(self, context):
        self.context = context

    def __call__(self, request):
        return [{
            "id": STORAGE_STICKER,
            "title": _("Storage location (50x30mm)"),
            "selected": True,
        }]
