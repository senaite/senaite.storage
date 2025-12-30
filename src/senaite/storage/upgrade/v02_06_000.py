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
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.storage import logger
from senaite.storage import PRODUCT_NAME
from senaite.storage.setuphandlers import setup_workflows

version = "2.6.0"
profile = "profile-{0}:default".format(PRODUCT_NAME)


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup  # noqa
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(PRODUCT_NAME)

    if ut.isOlderVersion(PRODUCT_NAME, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            PRODUCT_NAME, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(PRODUCT_NAME, ver_from,
                                                   version))

    # -------- ADD YOUR STUFF BELOW --------

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def remove_guard_scripts(tool):
    """Removes the guard zope scripts in favour of the generic guard_handler
    """
    portal = tool.aq_inner.aq_parent

    # re-import our own workflows
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "workflow")

    # Setup the custom workflows
    setup_workflows(portal)

    # Remove the senaite_storage_scripts skin layer
    scripts_id = "senaite_storage_scripts"
    skins_tool = api.get_tool("portal_skins")
    selections = skins_tool.getSkinSelections()
    if scripts_id in selections:
        del selections[scripts_id]
    if scripts_id in skins_tool:
        del skins_tool[scripts_id]


def setup_storage_controlpanel(tool):
    """Setup the storage control panel
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "plone.app.registry")
    setup.runImportStepFromProfile(profile, "controlpanel")
