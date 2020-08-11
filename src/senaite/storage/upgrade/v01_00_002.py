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

from senaite.storage import logger
from senaite.storage import PRODUCT_NAME
from senaite.storage.catalog import SENAITE_STORAGE_CATALOG
from senaite.storage.setuphandlers import post_install

from bika.lims import api
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.0.2'


INDEXES_TO_REMOVE = [
    # This was a ZCTextIndex. Replaced by `searchable_text` (TextIndexNG3)
    (SENAITE_STORAGE_CATALOG, "get_searchable_text"),
]


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(PRODUCT_NAME)

    if ut.isOlderVersion(PRODUCT_NAME, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            PRODUCT_NAME, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(PRODUCT_NAME, ver_from,
                                                   version))

    # -------- ADD YOUR STUFF BELOW --------
    # Remove stale indexes
    remove_stale_indexes(portal)

    # Reinstall
    post_install(setup)

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def remove_stale_indexes(portal):
    logger.info("Removing stale indexes ...")
    for catalog, index in INDEXES_TO_REMOVE:
        del_index(portal, catalog, index)


def del_index(portal, catalog_id, index_name):
    logger.info("Removing '{}' index from '{}' ..."
                .format(index_name, catalog_id))
    catalog = api.get_tool(catalog_id)
    if index_name not in catalog.indexes():
        logger.info("Index '{}' not in catalog '{}' [SKIP]"
                    .format(index_name, catalog_id))
        return
    catalog.delIndex(index_name)
    logger.info("Removing old index '{}' ...".format(index_name))
