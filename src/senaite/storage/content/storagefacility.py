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

from bika.lims import api
from bika.lims.browser.fields.addressfield import AddressField
from bika.lims.browser.widgets.addresswidget import AddressWidget
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.idserver import renameAfterCreation
from bika.lims.utils import get_email_link
from plone.app.folder.folder import ATFolder
from Products.Archetypes.atapi import registerType
from Products.Archetypes.Field import StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import StringWidget
from senaite.storage import PRODUCT_NAME
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.interfaces import IStorageFacility
from zope.interface import implements

Phone = StringField(
    name="Phone",
    widget=StringWidget(
        label=_("Phone")
    )
)

EmailAddress = StringField(
    name="EmailAddress",
    widget=StringWidget(
        label=_("Email Address"),
    ),
    validators=("isEmail",)
)

Address = AddressField(
    name="Address",
    widget=AddressWidget(
       label=_("Address"),
       render_own_label=True,
       showCopyFrom=False,
    ),
    subfield_validators={
        "country": "inline_field_validator",
        "state": "inline_field_validator",
        "district": "inline_field_validator",
    },
)

schema = BikaFolderSchema.copy() + Schema((
    Phone,
    EmailAddress,
    Address,
))


class StorageFacility(ATFolder):
    """Physical location or place where storage containers are located
    """
    implements(IStorageFacility)
    _at_rename_after_creation = True
    schema = schema

    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)

    def getPossibleAddresses(self):
        return [Address.getName()]

    def Description(self):
        phone = self.getPhone()
        if phone:
            phone = _("Tel: {}".format(phone))
        email = self.getEmailAddress()
        if email:
            email = _("Mail: {}".format(get_email_link(email)))
        address = self.getAddress()
        if address:
            address = ",".join(filter(None, address.values()))
        parts = filter(None, [email, phone, address])
        return ", ".join(map(api.safe_unicode, parts))


registerType(StorageFacility, PRODUCT_NAME)
