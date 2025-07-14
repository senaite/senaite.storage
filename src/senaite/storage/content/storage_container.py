# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from bika.lims import api
from plone.autoform import directives
from Products.CMFCore import permissions
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.content.storage_layout_container import \
    StorageLayoutContainer
from senaite.storage.content.storage_layout_container import \
    IStorageLayoutContainerSchema
from senaite.storage.interfaces import IStorageContainer
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.interface import implementer


class IStorageContainerSchema(IStorageLayoutContainerSchema):

    title = schema.TextLine(
        title=_(
            u"title_storage_container_title",
            default=u"Name"
        ),
        required=True)

    directives.widget("temperature", klass="numeric")
    temperature = schema.TextLine(
        title=_(
            u"title_storage_container_temperature",
            default=u"Temperature"
        ),
        description=_(
            u"description_storage_container_temperature",
            default=u"Expected temperature of this container"),
        required=False)

    directives.omitted(IEditForm, "description")
    description = schema.Text(
        title=_(
            u"title_storage_container_description",
            default=u"Description"
        ),
        required=False,
    )

    directives.omitted("rows")
    directives.omitted("columns")
    directives.omitted("positions_layout")
    directives.omitted("available_positions")


@implementer(IStorageContainer, IStorageContainerSchema)
class StorageContainer(StorageLayoutContainer):
    """A Storage container
    """
    _catalogs = [STORAGE_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def Description(self):
        temperature = self.getTemperature() or "-"
        return _(u"Expected temperature: %s °C" % temperature)

    @security.protected(permissions.View)
    def getTemperature(self):
        accessor = self.accessor("temperature")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setTemperature(self, value):
        mutator = self.mutator("temperature")
        value = str(api.to_float(value, 0))
        mutator(self, value)

    # BBB: AT schema field property
    Temperature = property(getTemperature, setTemperature)
