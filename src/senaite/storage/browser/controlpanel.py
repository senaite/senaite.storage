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

from bika.lims import api
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform import directives
from plone.supermodel import model
from plone.z3cform import layout
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.schema.registry import DataGridRow
from senaite.core.schema.vocabulary import to_simple_vocabulary
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.storage import _
from zope import schema
from zope.interface import Interface
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder


@provider(IContextSourceBinder)
def services_vocabulary(context):
    """Returns a SimpleVocabulary made of the active AnalysisService objects
    """
    catalog = api.get_tool(SETUP_CATALOG)
    query = {
        "portal_type": "AnalysisService",
        "is_active": True,
        "sort_on": "sortable_title",
        "sort_order": "ascending",
    }
    brains = catalog(query)
    items = [(api.get_uid(br), api.get_title(br)) for br in brains]
    return to_simple_vocabulary(items)


class IRetentionRule(Interface):
    """Schema for a single retention period rule row
    """

    service = schema.Choice(
        title=_(u"Analysis Service"),
        description=_(
            u"The Analysis Service for this rule"
        ),
        source=services_vocabulary,
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

    retention_days = schema.Int(
        title=_(u"Retention (days)"),
        description=_(
            u"Number of days for retention"
        ),
        required=True,
    )


class IStorageControlPanel(model.Schema):
    """Control panel Settings for senaite.storage
    """

    model.fieldset(
        "retention_rules",
        label=_(u"Retention Rules"),
        description=_(u""),
        fields=[
            "warning_days_before_expiration",
            "retention_period_rules",
        ],
    )

    model.fieldset(
        "retrieve_reasons",
        label=_(u"Retrieve Reasons"),
        description=_(u""),
        fields=[
            "require_retrieve_reason",
            "retrieve_reasons",
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
            default=u"Auto-retrieve primary sample"
        ),
        description=_(
            u"description_storage_settings_recover_primary",
            default=u"Select this option to automatically transition back the "
                    u"primary from 'stored' to its preceding status when all "
                    u"its partitions are retrieved."
        ),
        default=True,
    )

    warning_days_before_expiration = schema.Int(
        title=_(
            u"label_storage_settings_warning_days_expiration",
            default=u"Days before expiration"
        ),
        description=_(
            u"description_storage_settings_warning_days_expiration",
            default=u"Enter the number of days before a sample's retention "
                    u"period ends when it should be marked as approaching "
                    u"expiration. Samples within this threshold will display "
                    u"a visual indicator to help you quickly identify them."
        ),
        default=5,
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

    require_retrieve_reason = schema.Bool(
        title=_(
            u"label_storage_settings_require_retrieve_reason",
            default=u"Require retrieve reason"
        ),
        description=_(
            u"description_storage_settings_require_retrieve_reason",
            default=u"If enabled, users must select a reason when "
                    u"retrieving samples from storage. If disabled, "
                    u"selecting a reason is optional."
        ),
        default=False,
    )

    retrieve_reasons = schema.List(
        title=_(
            u"label_storage_settings_retrieve_reasons",
            default=u"Retrieve reasons"
        ),
        description=_(
            u"description_storage_settings_retrieve_reasons",
            default=u"Predefined list of reasons for retrieving "
                    u"samples from storage. When configured, users "
                    u"will be prompted to select a reason before the "
                    u"retrieve transition takes place."
        ),
        value_type=schema.TextLine(title=u"Reason"),
        required=False,
    )


class StorageControlPanelForm(RegistryEditForm):
    schema = IStorageControlPanel
    schema_prefix = "senaite.storage"
    label = _(u"header_storage_settings", default=u"Storage Settings")


StorageControlPanelView = layout.wrap_form(StorageControlPanelForm,
                                           ControlPanelFormWrapper)
