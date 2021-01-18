# -*- coding: utf-8 -*-

from plone.dexterity.content import Container
from plone.supermodel import model
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.api import get_storage_position_by_id
from senaite.storage.interfaces import IStoragePosition
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant


class IStoragePositionSchema(model.Schema):

    position_id = schema.TextLine(
        title=_(u"label_storage_position_id", default=u"Position ID"),
        description=_(u"Unique storage position identifier"),
        required=True,
    )

    @invariant
    def validate_position_id(data):
        """Checks if the location id is unique
        """
        # https://community.plone.org/t/dexterity-unique-field-validation
        context = getattr(data, "__context__", None)
        if context is not None:
            if context.position_id == data.position_id:
                # nothing changed
                return
        obj = get_storage_position_by_id(data.position_id)
        if obj is not None:
            raise Invalid(_("Storage position identifier must be unique"))


@implementer(IStoragePosition, IStoragePositionSchema)
class StoragePosition(Container):
    """A Storage position describes a location inside a facility
    """

    def get_position_id(self):
        return self.position_id
