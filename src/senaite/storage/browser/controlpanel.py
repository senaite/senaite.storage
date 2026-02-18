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

from bika.lims import senaiteMessageFactory as _s
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform import directives
from plone.supermodel import model
from plone.z3cform import layout
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.registry import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidget
from senaite.storage import _
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope import schema
from zope.interface import Interface
from zope.interface import implementer


class ControlPanelReferenceWidget(UIDReferenceWidget):
    """UIDReferenceWidget for use in control panel DataGrid rows.

    Overrides get_context to return the form context directly, avoiding
    the creation of a temporary object which fails for AT types when the
    form context is the Plone site root.
    """

    def get_context(self):
        form = self.get_form()
        return getattr(form, "context", None)


@implementer(IFieldWidget)
def ControlPanelReferenceWidgetFactory(field, request):
    return FieldWidget(field, ControlPanelReferenceWidget(request))


class IRetentionRule(Interface):
    """Schema for a single retention period rule row
    """

    directives.widget(
        "service",
        ControlPanelReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": ["AnalysisService"],
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        columns=[
            {"name": "Title", "label": _s("Title")},
            {"name": "getKeyword", "label": _s("Keyword")},
            {"name": "getCategoryTitle", "label": _s("Category")},
        ],
    )
    service = UIDReferenceField(
        title=_(u"Analysis Service"),
        description=_(
            u"The Analysis Service for this rule"
        ),
        allowed_types=("AnalysisService",),
        multi_valued=False,
        required=True,
    )

    result = schema.TextLine(
        title=_(u"Result"),
        description=_(
            u"Expected result value (leave empty for any result)"
        ),
        required=False,
        default=u"",
    )

    retention_days = schema.TextLine(
        title=_(u"Retention (days)"),
        description=_(
            u"Number of days for retention"
        ),
        required=True,
    )


class IStorageControlPanel(Interface):
    """Control panel Settings for senaite.storage
    """

    model.fieldset(
        "retention_rules",
        label=_(u"Retention Rules"),
        description=_(u""),
        fields=[
            "retention_period_rules",
        ],
    )

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

    directives.widget(
        "retention_period_rules",
        DataGridWidgetFactory,
        allow_reorder=True,
        auto_append=True)
    retention_period_rules = schema.List(
        title=_(
            u"label_storage_settings_retention_period_rules",
            default=u"Retention period rules"
        ),
        description=_(
            u"description_storage_settings_retention_period_rules",
            default=u"Configure default retention periods based on test "
                    u"and/or result criteria. When storing a sample, the "
                    u"system will suggest a retention period based on these "
                    u"rules."
        ),
        value_type=DataGridRow(
            title=u"Retention Rule",
            schema=IRetentionRule),
        required=False,
    )


class StorageControlPanelForm(RegistryEditForm):
    schema = IStorageControlPanel
    schema_prefix = "senaite.storage"
    label = _(u"header_storage_settings", default=u"Storage Settings")


StorageControlPanelView = layout.wrap_form(StorageControlPanelForm,
                                           ControlPanelFormWrapper)
