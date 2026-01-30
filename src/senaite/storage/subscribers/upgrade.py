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
from bika.lims.api import get_portal
from plone.dexterity.fti import DexterityFTI
from senaite.storage import is_installed
from senaite.storage import logger
from senaite.storage import PRODUCT_NAME
from senaite.storage.setuphandlers import setup_catalogs
from senaite.storage.setuphandlers import setup_user_groups
from senaite.storage.setuphandlers import setup_workflows


def afterUpgradeStepHandler(event):
    """Event handler that is executed after running an upgrade step of senaite.core
    """
    if not is_installed():
        return

    logger.info("Run {}.afterUpgradeStepHandler ...".format(PRODUCT_NAME))
    portal = get_portal()
    setup = portal.portal_setup  # noqa

    profile = "profile-{0}:default".format(PRODUCT_NAME)

    # Only run typeinfo import if all types are already migrated to DX
    # to avoid errors when trying to apply DX properties to AT types
    if types_migrated_to_dx(portal):
        setup.runImportStepFromProfile(profile, "typeinfo")
    else:
        logger.info("Skipping typeinfo import - AT to DX migration pending")

    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "workflow")

    # Setup catalogs
    setup_catalogs(portal)

    # setup user groups
    setup_user_groups(portal)

    # Setup workflows
    setup_workflows(portal)

    logger.info("Run {}.afterUpgradeStepHandler [DONE]".format(PRODUCT_NAME))


def types_migrated_to_dx(portal):
    """Check if all storage types have been migrated to Dexterity
    """
    pt = api.get_tool("portal_types")
    storage_types = [
        "StorageRootFolder",
        "StorageFacility",
        "StorageContainer",
        "StorageSamplesContainer",
    ]

    for type_name in storage_types:
        fti = pt.getTypeInfo(type_name)
        if not fti:
            # Type doesn't exist yet - not migrated
            return False
        if not isinstance(fti, DexterityFTI):
            # Still an AT type - not migrated
            logger.info("Type '{}' is still AT, migration needed".format(type_name))
            return False

    return True
