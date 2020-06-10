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
# Copyright 2019-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Archetypes.Field import StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.atapi import registerType
from bika.lims.browser.fields.addressfield import AddressField
from bika.lims.browser.widgets.addresswidget import AddressWidget
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.idserver import renameAfterCreation
from plone.app.folder.folder import ATFolder
from senaite.storage import PRODUCT_NAME
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.interfaces import IStorageFacility, IStorageLayoutContainer
from zope.interface import implements

Phone = StringField(
    name = 'Phone',
    widget = StringWidget(
        label = _("Phone")
    )
)

EmailAddress = StringField(
    name = 'EmailAddress',
    widget = StringWidget(
        label=_("Email Address"),
    ),
    validators = ('isEmail',)
)

Address = AddressField(
    name = 'Address',
    widget = AddressWidget(
       label=_("Address"),
       render_own_label=True,
       showCopyFrom=False,
    ),
    subfield_validators = {
        'country': 'inline_field_validator',
        'state': 'inline_field_validator',
        'district': 'inline_field_validator',
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
    displayContentsTab = False
    schema = schema

    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)

    def getPossibleAddresses(self):
        return [Address.getName()]

    def get_capacity(self):
        """Returns the total number of containers that belong to this facility
        """
        return len(self.get_layout_containers())

    def get_available_positions(self):
        """Returns the number of available containers
        """
        return self.get_capacity()

    def get_layout_containers(self):
        """Returns the containers that belong to this facility and implement
        IStorageLayoutContainer
        """
        return filter(lambda obj: IStorageLayoutContainer.providedBy(obj),
                            self.objectValues())

    def get_samples_capacity(self):
        """Returns the total number of samples this facility can store
        """
        return sum(map(lambda con: con.get_samples_capacity(),
                       self.get_layout_containers()))

    def get_samples_utilization(self):
        """Returns the total number of samples this facility actually stores
        """
        return sum(map(lambda con: con.get_samples_utilization(),
                       self.get_layout_containers()))


registerType(StorageFacility, PRODUCT_NAME)
