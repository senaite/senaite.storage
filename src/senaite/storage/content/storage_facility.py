# -*- coding: utf-8 -*-

import re
from string import Template

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims.api.mail import is_valid_email_address
from bika.lims.interfaces import IDoNotSupportSnapshots
from bika.lims.utils import get_email_link
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.content.base import Container
from senaite.core.interfaces import IHideActionsMenu
from senaite.core.schema import AddressField
from senaite.core.schema import PhoneField
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.z3cform.widgets.phone import PhoneWidgetFactory
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.interfaces import IStorageFacility
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant

POSSIBLE_ADDRESSES = [PHYSICAL_ADDRESS]

INFO_TEMPLATE = Template(u"""<address>
  $address<br/>
  $zip $city<br/>
  $country<br/>
  $email<br/>
  $phone
</address>
""")

INFO_CONTEXT = {
    "address": "",
    "zip": "",
    "city": "",
    "country": "",
    "email": "",
    "phone": "",
}


class IStorageFacilitySchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=_(
            u"title_storage_facility_title",
            default=u"Name"
        ),
        required=True,
    )

    directives.omitted(IEditForm, "description")
    description = schema.Text(
        title=_(
            u"title_storage_facility_description",
            default=u"Description"
        ),
        required=False,
    )

    directives.widget("phone", PhoneWidgetFactory)
    phone = PhoneField(
        title=_(
            u"label_storage_facility_phone",
            default=u"Phone Number"),
        description=_(
            u"description_storage_facility_phone",
            default=u"The phone number of this storage facility"),
        required=False,
    )

    email = schema.TextLine(
        title=_(
            u"label_storage_facility_email",
            default=u"Email Address"
        ),
        description=_(
            u"description_storage_facility_email",
            default=u"The email address of this storage facility"),
        required=False,
    )

    address = AddressField(
        title=_("Address"),
        address_types=[
            PHYSICAL_ADDRESS,
        ]
    )

    @invariant
    def validate_email(data):
        """Checks if the email is correct
        """
        if not data.email:
            return
        if not is_valid_email_address(data.email):
            raise Invalid(_("Email is invalid"))


@implementer(IStorageFacility, IStorageFacilitySchema,
             IDoNotSupportSnapshots, IHideActionsMenu)
class StorageFacility(Container):
    """Physical location or place where storage containers are located
    """
    _catalogs = [STORAGE_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def Description(self):
        context = dict(INFO_CONTEXT)
        phone = self.getPhone() or ""
        if phone:
            context["phone"] = _("Tel: {}".format(phone))
        email = self.getEmailAddress() or ""
        if email:
            context["email"] = _("Mail: {}".format(get_email_link(email)))
        for record in self.getAddress():
            if record.get("type") == PHYSICAL_ADDRESS:
                context.update(record)
        html = INFO_TEMPLATE.safe_substitute(context)
        return re.sub(r"^\s*<br/>\s*$", "", html, flags=re.MULTILINE)

    @security.protected(permissions.View)
    def getPhone(self):
        accessor = self.accessor("phone")
        value = accessor(self) or ""
        return api.to_utf8(value)

    @security.protected(permissions.ModifyPortalContent)
    def setPhone(self, value):
        mutator = self.mutator("phone")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    Phone = property(getPhone, setPhone)

    @security.protected(permissions.View)
    def getEmailAddress(self):
        accessor = self.accessor("email")
        value = accessor(self) or ""
        return api.to_utf8(value)

    @security.protected(permissions.ModifyPortalContent)
    def setEmailAddress(self, value):
        mutator = self.mutator("email")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    EmailAddress = property(getEmailAddress, setEmailAddress)

    @security.protected(permissions.View)
    def getAddress(self):
        accessor = self.accessor("address")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAddress(self, value):
        mutator = self.mutator("address")
        mutator(self, value)

    # BBB: AT schema field property
    Address = property(getAddress, setAddress)
