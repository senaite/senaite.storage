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

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from senaite.storage import _
from zope import schema
from zope.interface import Interface


class IStorageControlPanel(Interface):
    """Control panel Settings for senaite.storage
    """

    store_primary = schema.Bool(
        title=_(
            u"label_storage_settings_store_primary",
            default=u"Auto-store primary sample"
        ),
        description=_(
            u"description_storage_settings_store_primary",
            default=u"Select this option to automatically transition the "
                    u"primary sample to 'stored' status when it does not have "
                    u"analyses assigned and all its partitions are stored."
        ),
        default=True,
    )

    recover_primary = schema.Bool(
        title=_(
            u"label_storage_settings_recover_primary",
            default=u"Auto-recover primary sample"
        ),
        description=_(
            u"description_storage_settings_recover_primary",
            default=u"Select this option to automatically transition back the "
                    u"primary from 'stored' to its preceding status when all "
                    u"its partitions are recovered."
        ),
        default=True,
    )


class StorageControlPanelForm(RegistryEditForm):
    schema = IStorageControlPanel
    schema_prefix = "senaite.storage"
    label = _(u"header_storage_settings", default=u"Storage Settings")


StorageControlPanelView = layout.wrap_form(StorageControlPanelForm,
                                           ControlPanelFormWrapper)
