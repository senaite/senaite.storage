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
# Copyright 2019-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.dexterity.content import Container
from plone.supermodel import model
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.interfaces import IStoragePosition
from zope import schema
from zope.interface import implementer


class IStoragePositionSchema(model.Schema):

    title = schema.TextLine(
        title=_(u"Name"),
        description=_(
            u"The name of the storage position, e.g. Room 12/3"),
        required=True)

    description = schema.Text(
        title=u"Description",
        description=_(
            u"Description of the storage position that is shown in listings"),
        required=False)


@implementer(IStoragePosition, IStoragePositionSchema)
class StoragePosition(Container):
    """A Storage position describes a location inside a facility
    """
    _catalogs = [STORAGE_CATALOG]
