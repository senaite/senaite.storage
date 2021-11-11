# -*- coding: utf-8 -*-

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
