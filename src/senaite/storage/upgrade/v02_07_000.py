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

from bika.lims.utils import tmpID
from bika.lims import api
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContent
from senaite.core.interfaces import IContentMigrator
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.storage import PRODUCT_NAME
from senaite.storage import logger
from senaite.storage.catalog import STORAGE_CATALOG
from zope.component import getMultiAdapter

version = "2.7.0"
profile = "profile-{0}:default".format(PRODUCT_NAME)

REMOVE_AT_TYPES = [
    "StorageFacility",
    "StorageContainer",
    "StorageSamplesContainer",
    "StorageRootFolder",
]


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


def remove_at_portal_types(tool):
    """Remove obsolete AT portal type information
    """
    logger.info("Remove AT types from portal_types tool ...")
    pt = api.get_tool("portal_types")
    for type_name in REMOVE_AT_TYPES:
        fti = pt.getTypeInfo(type_name)
        # keep DX FTIs
        if isinstance(fti, DexterityFTI):
            logger.info("Type '{}' is already a DX FTI".format(fti))
            continue
        elif not fti:
            # Removed already
            continue
        pt.manage_delObjects(fti.getId())

    # remove from AT's factory tool as well. This is necessary for the AT's
    # factory_tool to not shortcut `createObject?type_name=` on object creation
    ft = api.get_tool("portal_factory")
    at_types = ft.getFactoryTypes().keys()
    at_types = filter(lambda name: name not in REMOVE_AT_TYPES, at_types)
    ft.manage_setPortalFactoryTypes(listOfTypeIds=at_types)

    logger.info("Remove AT types from portal_types tool ... [DONE]")


def migrate_storage_facilities_to_dx(tool):
    """Converts existing storage facility to DX
    """
    logger.info("Convert Storage Facilities to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    root_folder = api.get_portal().get("senaite_storage")
    if not root_folder:
        return

    for sf in root_folder.objectValues("StorageFacility"):
        if not api.is_at_content(sf):
            continue
        logger.info("Migrating facility '%s'" % sf.Title())
        migrate_storage_facility_to_dx(sf, root_folder)
        logger.info("Migrating facility '%s' [DONE]" % sf.Title())

    logger.info("Convert Storage Facilities to Dexterity [DONE]")


def migrate_storage_facility_to_dx(src, destination):
    """Migrate a single storage facility
    """
    target_id = tmpID()
    portal_type = "StorageFacility"

    # cretate the new facility
    target = createContent(portal_type, id=target_id)
    destination._setObject(target_id, target)
    target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or "")
    target.phone = api.safe_unicode(src.getPhone() or "")
    target.email = api.safe_unicode(src.getEmailAddress() or "")

    address = dict(src.getAddress())
    address["type"] = PHYSICAL_ADDRESS
    target.setAddress(address)

    cb = src.manage_copyObjects(ids=src.objectIds())
    target.manage_pasteObjects(cb)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # copy auditlog
    migrator.copy_snapshots(src, target)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)


def migrate_storage_containers_to_dx(tool):
    """Converts existing storage containers to DX
    """
    logger.info("Convert Storage Containers to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    query = {
        "portal_type": "StorageContainer",
    }
    results = api.search(query, STORAGE_CATALOG)

    for brain in results:
        obj = api.get_object(brain)
        if not api.is_at_content(obj):
            continue
        logger.info("Migrating storage container '%s'" % obj.Title())
        destination = api.get_parent(obj)
        migrate_storage_container_to_dx(obj, destination)
        logger.info("Migrating storage container '%s' [DONE]" % obj.Title())

    logger.info("Convert Storage Containers to Dexterity [DONE]")


def migrate_storage_container_to_dx(src, destination):
    """Migrate a single storage facility
    """
    target_id = tmpID()
    portal_type = "StorageContainer"

    # cretate the new facility
    target = createContent(portal_type, id=target_id)
    destination._setObject(target_id, target)
    target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or "")
    target.temperature = src.getTemperature() or 0.0

    cb = src.manage_copyObjects(ids=src.objectIds())
    target.manage_pasteObjects(cb)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # copy auditlog
    migrator.copy_snapshots(src, target)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)


def migrate_storage_sample_containers_to_dx(tool):
    """Converts existing storage containers to DX
    """
    logger.info("Convert Storage Sample Containers to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    query = {
        "portal_type": "StorageSamplesContainer",
    }
    results = api.search(query, STORAGE_CATALOG)

    for brain in results:
        obj = api.get_object(brain)
        if not api.is_at_content(obj):
            continue
        logger.info("Migrating storage samples container '%s'" % obj.Title())
        destination = api.get_parent(obj)
        migrate_storage_samples_container_to_dx(obj, destination)
        logger.info("Migrating storage samples container '%s' [DONE]" %
                    obj.Title())

    logger.info("Convert Storage Sample Containers to Dexterity [DONE]")


def migrate_storage_samples_container_to_dx(src, destination):
    """Migrate a single storage samples container
    """
    target_id = tmpID()
    portal_type = "StorageSamplesContainer"

    # cretate the new facility
    target = createContent(portal_type, id=target_id)
    destination._setObject(target_id, target)
    target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or u"")
    target.description = api.safe_unicode(src.Description() or u"")
    target.rows = src.getColumns() or 1
    target.columns = src.getRows() or 1
    target.positions_layout = src.getPositionsLayout() or []
    target.available_positions = src.getAvailablePositions() or []

    cb = src.manage_copyObjects(ids=src.objectIds())
    target.manage_pasteObjects(cb)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # copy auditlog
    migrator.copy_snapshots(src, target)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)


def migrate_storage_root_folder_to_dx(tool):
    """Migrate the storage root folder to DX
    """
    logger.info("Convert Storage Root Folder to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    target_id = tmpID()
    portal_type = "StorageRootFolder"
    portal = tool.aq_inner.aq_parent

    src = portal._getOb("senaite_storage")
    if api.is_dexterity_content(src):
        logger.info("Storage Root Folder is already a Dexterity type, exiting")
        return

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # cretate the new facility
    target = createContent(portal_type, id=target_id)
    portal._setObject(target_id, target)
    target = portal._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or u"")
    target.description = api.safe_unicode(src.Description() or u"")

    cb = src.manage_copyObjects(ids=src.objectIds())
    target.manage_pasteObjects(cb)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # copy auditlog
    migrator.copy_snapshots(src, target)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    logger.info("Convert Storage Root Folder to Dexterity [DONE]")
