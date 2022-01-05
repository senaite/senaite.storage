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
from Products.ZCatalog.ProgressHandler import ZLogHandler
from senaite.core.api.catalog import add_column
from senaite.core.api.catalog import add_index
from senaite.core.api.catalog import get_columns
from senaite.core.api.catalog import get_index
from senaite.core.api.catalog import get_indexes
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.storage import PRODUCT_NAME
from senaite.storage import logger
from senaite.storage.setuphandlers import post_install
from senaite.storage.setuphandlers import setup_catalogs

version = "2.1.0"


MIGRATE_CATALOGS = [
    ("senaite_storage_catalog", "senaite_catalog_storage"),
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

    # Reinstall
    post_install(setup)

    # https://github.com/senaite/senaite.storage/pull/30
    migrate_catalogs(portal)

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def migrate_catalogs(portal):
    """Migrate catalogs to Senaite
    """
    logger.info("Migrate storage catalogs...")
    # 1. Install new core catalogs
    setup_catalogs(portal)

    # 3. Migrate old -> new indexes
    for src_cat_id, dst_cat_id in MIGRATE_CATALOGS:
        logger.info("Migrating catalog %s -> %s" %
                    (src_cat_id, dst_cat_id))

        src_cat = getattr(portal, src_cat_id, None)
        dst_cat = getattr(portal, dst_cat_id, None)

        if src_cat is None:
            logger.info("Source catalog '%s' not found [SKIP]")
            continue

        # ensure indexes
        for index in get_indexes(src_cat):
            if index not in get_indexes(dst_cat):
                index_obj = get_index(src_cat, index)
                index_type = index_obj.__class__.__name__
                # convert TextIndexNG3 to ZCTextIndex
                if index_type == "TextIndexNG3":
                    index_type = "ZCTextIndex"
                add_index(dst_cat, index, index_type)
                logger.info("Added missing index %s('%s') to %s"
                            % (index_type, index, dst_cat_id))

        # ensure columns
        for column in get_columns(src_cat):
            if column not in get_columns(dst_cat):
                add_column(dst_cat, column)
                logger.info("Added missing column %s to %s"
                            % (column, dst_cat_id))

        # rebuild the catalog
        dst_cat.clearFindAndRebuild()

        # delete old catalog
        portal.manage_delObjects([src_cat_id])

    # Update archetype tool
    logger.info("Update catalog mapping in archetype_tool")
    at = api.get_tool("archetype_tool")
    for portal_type, catalogs in at.catalog_map.items():
        at.setCatalogsByType(portal_type, catalogs)

    # we need to refresh the sample catalog, otherwise the stored samples are
    # not displayed
    logger.info("Refresh sample catalog")
    sample_catalog = api.get_tool(SAMPLE_CATALOG)
    pghandler = ZLogHandler(100)
    sample_catalog.refreshCatalog(pghandler=pghandler)

    logger.info("Migrate storage catalogs [DONE]")
