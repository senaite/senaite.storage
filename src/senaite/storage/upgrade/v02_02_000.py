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
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.storage import logger
from senaite.storage import PRODUCT_NAME

version = "2.2.0"
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
    setup.runImportStepFromProfile(profile, "workflow")
    update_storage_role_mappings(portal)

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def update_storage_role_mappings(portal):
    """Update the role mappings of senaite storage's root folder
    """
    logger.info("Fixing permissions for storage's root folder ...")
    wf_tool = api.get_tool("portal_workflow")
    wf_id = "senaite_storage_folder_workflow"
    workflow = wf_tool.getWorkflowById(wf_id)
    storage_root = portal.senaite_storage
    workflow.updateRoleMappingsFor(storage_root)
    storage_root.reindexObjectSecurity()
    logger.info("Fixing permissions for storage's root folder [DONE]")
