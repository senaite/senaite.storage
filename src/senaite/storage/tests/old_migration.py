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
"""The migration of the storage contents to Dexterity as released before
senaite.storage#80, kept to test the restore of the sites it migrated.

It copied the contents of the migrated objects, so they got new UIDs, did
not migrate the dimensions and layout of the storage containers and swapped
the rows and columns of the samples containers. It ran with the event
handlers of that time, which did not add a container to the layout of its
parent when it was added.

NOTE: Remove this module, with the `StorageMigration` doctest, together with
the AT classes and the 2.7.0 migration steps.
"""

from contextlib import contextmanager

from bika.lims import api
from bika.lims.utils import tmpID
from plone.dexterity.utils import createContent
from senaite.core.interfaces import IContentMigrator
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.storage import logger
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.interfaces import IStorageLayoutContainer
from senaite.storage.subscribers import StorageContentAddedEventHandler
from senaite.storage.subscribers import \
    StorageContentCreatedByAPIEventHandler
from senaite.storage.upgrade.v02_07_000 import profile
from senaite.storage.upgrade.v02_07_000 import remove_at_portal_types
from senaite.core.events.lifecycle import IAfterAPICreatedObjectEvent
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.lifecycleevent.interfaces import IObjectAddedEvent


def former_added_handler(container, event):
    """The handler for added containers of that time: it rebuilt the layout
    of the container, but did not add it to the layout of its parent
    """
    container.rebuild_layout()


@contextmanager
def former_event_handlers():
    """Runs the code with the event handlers for added containers of the
    time of the former migration
    """
    gsm = getGlobalSiteManager()
    current = [
        (StorageContentAddedEventHandler, IObjectAddedEvent),
        (StorageContentCreatedByAPIEventHandler,
         IAfterAPICreatedObjectEvent),
    ]
    for handler, event in current:
        gsm.unregisterHandler(handler, (IStorageLayoutContainer, event))
    gsm.registerHandler(former_added_handler,
                        (IStorageLayoutContainer, IObjectAddedEvent))
    try:
        yield
    finally:
        gsm.unregisterHandler(former_added_handler,
                              (IStorageLayoutContainer, IObjectAddedEvent))
        for handler, event in current:
            gsm.registerHandler(handler, (IStorageLayoutContainer, event))


def migrate(tool):
    """Runs the former migration steps 2700 to 2704
    """
    with former_event_handlers():
        migrate_storage_facilities_to_dx(tool)
        migrate_storage_containers_to_dx(tool)
        migrate_storage_sample_containers_to_dx(tool)
        migrate_storage_root_folder_to_dx(tool)


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
    for key in list(address.keys()):
        address[key] = api.safe_unicode(address.get(key, u""))
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
