# -*- coding: utf-8 -*-

from plone.dexterity.content import Container
from plone.supermodel import model
from senaite.storage.interfaces import IStoragePosition
from zope.interface import implementer


class IStoragePositionSchema(model.Schema):
    pass


@implementer(IStoragePosition, IStoragePositionSchema)
class StoragePosition(Container):
    """A Storage position describes a location inside a facility
    """
