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

from Acquisition import aq_base
from bika.lims import api
from bika.lims.utils import tmpID
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContent
from Products.CMFCore.indexing import processQueue
from senaite.core.api import snapshot as snapshot_api
from senaite.core.api import workflow as wapi
from senaite.core.interfaces import IContentMigrator
from senaite.core.migration.migrator import ATTRIBUTE_STORAGE
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.setuphandlers import add_catalog_index
from senaite.core.subscribers.auditlog import reindex_object as \
    reindex_auditlog
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.core.workflow import SAMPLE_WORKFLOW
from senaite.storage import logger
from senaite.storage import PRODUCT_NAME
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.config import STORAGE_WORKFLOW_ID
from senaite.storage.interfaces import IStorageLayoutContainer
from senaite.storage.interfaces import IStorageSamplesContainer
from senaite.storage.setuphandlers import display_in_nav
from senaite.storage.setuphandlers import setup_roles
from senaite.storage.setuphandlers import setup_user_groups
from senaite.storage.setuphandlers import setup_workflows
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from senaite.core.catalog import SAMPLE_CATALOG
import transaction

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


def move_contents(src, target):
    """Moves the contents of the source object into the target

    The contents are moved rather than copied, because a copy gets a new UID
    and the layout of a storage container refers to its contents by UID
    """
    for obj in src.objectValues():
        # the workflow of the storage contents does not grant the permission
        # to delete them, which a cut and paste requires
        api.move_object(obj, target, check_constraints=False)


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

    move_contents(src, target)

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

    # the parent took the new container in, with its temporary UID
    if IStorageLayoutContainer.providedBy(destination):
        destination.remove_object(target, notify_parent=False)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or "")
    target.temperature = src.getTemperature() or 0.0
    target.rows = src.getRows() or 1
    target.columns = src.getColumns() or 1
    target.positions_layout = src.getPositionsLayout() or []
    target.available_positions = src.getAvailablePositions() or []

    move_contents(src, target)

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

    # the parent took the new container in, with its temporary UID
    if IStorageLayoutContainer.providedBy(destination):
        destination.remove_object(target, notify_parent=False)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or u"")
    target.description = api.safe_unicode(src.Description() or u"")
    target.rows = src.getRows() or 1
    target.columns = src.getColumns() or 1
    target.positions_layout = src.getPositionsLayout() or []
    target.available_positions = src.getAvailablePositions() or []

    move_contents(src, target)

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

    move_contents(src, target)

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


def display_storage_navbar(tool):
    """Displays the storage's root folder in the navigation bar
    """
    logger.info("Display storage in navigation bar ...")
    portal = api.get_portal()
    display_in_nav(portal.senaite_storage)
    logger.info("Display storage in navigation bar [DONE]")


@upgradestep(PRODUCT_NAME, version)
def setup_storage_roles_and_groups(tool):
    """Set up storage-specific roles and user groups.

    We add the @upgradestep decorator because we reapply storage-specific
    workflow changes in `setuphandlers.update_workflow`, which may otherwise
    overwrite workflow customizations introduced by more specific add-ons.
    Using this decorator ensures that upgrade subscribers from other add-ons
    are executed afterwards.
    """
    logger.info("Setup storage-specific roles and groups ...")

    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup  # noqa

    # import rolemap and workflow definitions
    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "workflow")

    # setup roles permissions for portal
    setup_roles(portal)

    # setup user groups
    setup_user_groups(portal)

    # setup workflows
    setup_workflows(portal)

    # catalog indexes to reindex after updating role mappings
    idxs = ["allowedRolesAndUsers"]

    # update role mappings for storage's root folder
    storage_folder = portal.senaite_storage
    workflow = wapi.get_workflow("senaite_storage_folder_workflow")
    workflow.updateRoleMappingsFor(storage_folder)
    storage_folder.reindexObject(idxs=idxs)

    # update role mappings for storage-specific objects
    logger.info("Updating role mappings of storage objects ...")
    workflow = wapi.get_workflow(STORAGE_WORKFLOW_ID)
    cat = api.get_tool(STORAGE_CATALOG)
    brains = cat()
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Updating role mappings of storage objects {0}/{1}"
                        .format(num, total))
            transaction.savepoint(optimistic=True)

        ob = api.get_object(brain)
        workflow.updateRoleMappingsFor(ob)
        cat.catalog_object(ob, idxs=idxs, update_metadata=0)
        ob._p_deactivate()  # noqa

    # update role mappings for samples in 'stored' status
    logger.info("Updating role mappings of samples ...")
    workflow = wapi.get_workflow(SAMPLE_WORKFLOW)
    cat = api.get_tool(SAMPLE_CATALOG)
    brains = cat(review_state="stored")
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Updating role mappings of samples {0}/{1}"
                        .format(num, total))
            transaction.savepoint(optimistic=True)

        if num and num % 1000 == 0:
            # Updating role mappings on samples can exhaust all available RAM,
            # even if objects are explicitly deactivated. This happens because
            # DCWorkflow's updateRoleMappings wakes up objects across the
            # entire hierarchy in order to resolve inherited permissions via
            # acquisition. Therefore, we deactivate here all unmodified objects
            # from the cache of the current database connection
            logger.info("Flushing deactivated objects from cache ...")
            portal._p_jar.cacheMinimize()  # noqa

        ob = api.get_object(brain)
        workflow.updateRoleMappingsFor(ob)
        cat.catalog_object(ob, idxs=idxs, update_metadata=0)
        ob._p_deactivate()  # noqa

    logger.info("Setup storage-specific roles and groups [DONE]")


def setup_retention_period_rules(tool):
    """Register retention period rules field in the registry
    """
    logger.info("Setup retention period rules ...")

    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup  # noqa
    setup.runImportStepFromProfile(profile, "plone.app.registry")

    logger.info("Setup retention period rules [DONE]")


def setup_past_retention_filter(tool):
    """Adds a DateIndex in samples catalog ('getStorageExpiryDate') to allow
    date range searches by retention period expiry date
    """
    logger.info("Setup past retention filter ...")
    portal = tool.aq_inner.aq_parent

    # Add the index (without reindex)
    cat = api.get_tool(SAMPLE_CATALOG)
    idx_id = "getStorageExpiryDate"
    add_catalog_index(cat, idx_id, "", "DateIndex")

    # reindex this index only for samples in stored status
    brains = cat(review_state="stored")
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Processed objects: {0}/{1}".format(num, total))
            transaction.savepoint()

        obj = api.get_object(brain)
        obj.reindexObject(idxs=[idx_id])
        obj._p_deactivate()

    logger.info("Setup past retention filter [DONE]")


def setup_days_before_expiration(tool):
    """Add 'Days before expiration' setting in control panel
    """
    logger.info("Setup days before expiration ...")

    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup  # noqa
    setup.runImportStepFromProfile(profile, "plone.app.registry")

    logger.info("Setup days before expiration [DONE]")


def setup_retrieve_reasons(tool):
    """Register retrieve reason fields in the registry
    """
    logger.info("Setup retrieve reasons ...")

    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup  # noqa
    setup.runImportStepFromProfile(profile, "plone.app.registry")

    logger.info("Setup retrieve reasons [DONE]")


def setup_storage_sticker_action(tool):
    """Register the 'Stickers preview' object action on storage location types
    """
    logger.info("Setup storage sticker action ...")

    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup  # noqa
    setup.runImportStepFromProfile(profile, "typeinfo")

    logger.info("Setup storage sticker action [DONE]")


def rename_recover_to_retrieve(tool):
    """Renames the user-facing term 'recover' to 'retrieve', which aligns with
    ISO 17025 and ISO 15189 standard terminology for the process of taking
    samples out of storage. Internal transition IDs and permission strings
    remain unchanged for backwards compatibility.
    """
    logger.info("Recover --> Retrieve ...")
    portal = tool.aq_inner.aq_parent

    # Update the sample workflow (transition title/action)
    setup_workflows(portal)

    # Re-import the storage workflow definition (transition title/action)
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "workflow")

    logger.info("Recover --> Retrieve [DONE]")


def reindex_date_stored(tool):
    """Reindex 'getDateStored' for the samples already in storage

    getDateStored now returns a DateTime instead of a pre-formatted string,
    so the index and metadata column of samples already stored need to be
    rebuilt for the "Date stored" column to show up.
    """
    logger.info("Reindex date stored ...")

    cat = api.get_tool(SAMPLE_CATALOG)
    brains = cat(review_state="stored")
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Processed objects: {0}/{1}".format(num, total))
            transaction.savepoint()

        obj = api.get_object(brain)
        obj.reindexObject(idxs=["getDateStored"])
        obj._p_deactivate()

    logger.info("Reindex date stored [DONE]")


def restore_migrated_layouts(tool):
    """Restores the dimensions and layouts the migration to DX lost

    The migration swapped the rows and columns of samples containers, did not
    migrate the dimensions and layout of storage containers, and gave the
    contents of every migrated object a new UID, so the layouts of storage
    containers referred to children that no longer exist. The attributes of
    the AT objects are still kept in an annotation, so they can be restored.
    """
    logger.info("Restore the layouts of migrated containers ...")

    query = {"portal_type": ["StorageContainer", "StorageSamplesContainer"]}
    brains = api.search(query, STORAGE_CATALOG)
    containers = map(api.get_object, brains)

    # only the containers migrated from AT keep the attributes of the AT
    # object, the others have nothing to restore
    migrated = filter(get_migrated_attributes, containers)
    if not migrated:
        logger.info("Restore the layouts of migrated containers: no container "
                    "migrated from AT [SKIP]")
        return

    # children first, so the parents take their restored capacity in
    migrated.sort(key=lambda obj: len(obj.getPhysicalPath()), reverse=True)

    # samples stored in any container now
    stored = set()
    for container in containers:
        if IStorageSamplesContainer.providedBy(container):
            stored.update(container.get_samples_uids())

    # ids of the objects the former migration copied, by their former UID
    original_ids = get_original_ids(api.get_portal().senaite_storage)

    total = len(migrated)
    for num, container in enumerate(migrated):
        if num and num % 100 == 0:
            logger.info("Restore the layouts of migrated containers {}/{}"
                        .format(num, total))
        restore_migrated_layout(container, stored, original_ids)

    logger.info("Restore the layouts of migrated containers [DONE]")


def get_migrated_attributes(obj):
    """Returns the attributes the migration kept from the AT object
    """
    storage = IAnnotations(obj).get(ATTRIBUTE_STORAGE)
    return dict(storage or {})


def get_occupied(layout):
    """Returns the occupied items of the layout as (row, column, uid)
    """
    occupied = []
    for item in layout or []:
        uid = item.get("uid")
        if not uid:
            continue
        row = api.to_int(item.get("row"), default=-1)
        column = api.to_int(item.get("column"), default=-1)
        occupied.append((row, column, uid))
    return occupied


def get_original_ids(root):
    """Returns the ids of the storage objects by the UIDs they ever had

    The former migration copied the contents of the migrated objects, so
    they got new UIDs, while the layouts of the containers kept the former
    ones. It kept the attributes of each AT object in an annotation, its
    folder tree included, so the original objects are still there, with
    their ids and UIDs.

    :param root: the storage root folder
    :returns: dict of UID -> id
    """
    ids = {}
    seen = set()

    def walk(obj):
        obj = aq_base(obj)
        if id(obj) in seen:
            return
        seen.add(id(obj))
        annotations = getattr(obj, "__annotations__", None) or {}
        attributes = annotations.get(ATTRIBUTE_STORAGE) or {}
        for tree in (getattr(obj, "_tree", None), attributes.get("_tree")):
            if not tree:
                continue
            for child_id, child in tree.items():
                uid = getattr(aq_base(child), "_at_uid", None) or \
                    getattr(aq_base(child), "_plone.uuid", None)
                if uid:
                    ids.setdefault(uid, child_id)
                walk(child)

    walk(root)
    return ids


def get_migrated_dimensions(container, rows, columns):
    """Returns the dimensions the former migration left to a container that
    had the given ones in AT: swapped for a samples container, the default
    ones for a storage container
    """
    if IStorageSamplesContainer.providedBy(container):
        return (columns, rows)
    return (1, 1)


def get_current_items(container, original_ids):
    """Returns the occupied positions of the container, as a list of
    (row, column, object), and the ones whose object cannot be found, as a
    list of (row, column, UID)
    """
    found = []
    missing = []
    for row, column, uid in get_occupied(container.getPositionsLayout()):
        obj = api.get_object_by_uid(uid, default=None)
        if obj is None and not IStorageSamplesContainer.providedBy(container):
            # the former UID of a child the former migration copied
            obj = get_child_container(container, uid, original_ids)
        if obj is None:
            missing.append((row, column, uid))
        else:
            found.append((row, column, obj))
    return found, missing


def get_at_items(container, attributes, stored, original_ids):
    """Returns the occupied positions of the AT layout whose object belongs to
    the container now, as a list of (row, column, object)

    For a samples container, these are the samples that are still stored but
    in no container. For a storage container, the containers it holds, that
    kept their UID or got a new one when the former migration copied them.
    """
    if IStorageSamplesContainer.providedBy(container):
        def resolve(uid):
            if uid in stored:
                return None
            obj = api.get_object_by_uid(uid, default=None)
            if obj is None or api.get_review_status(obj) != "stored":
                return None
            return obj
    else:
        def resolve(uid):
            return get_child_container(container, uid, original_ids)

    items = []
    for row, column, uid in get_occupied(attributes.get("PositionsLayout")):
        obj = resolve(uid)
        if obj is not None:
            items.append((row, column, obj))
    return items


def get_child_containers(container):
    """Returns the storage containers the container holds
    """
    return filter(IStorageLayoutContainer.providedBy,
                  container.objectValues())


def get_child_container(container, uid, original_ids):
    """Returns the storage container the container holds with the given UID,
    or the one that was copied from the object with this UID
    """
    for child in get_child_containers(container):
        if api.get_uid(child) == uid:
            return child
        if api.get_id(child) == original_ids.get(uid):
            return child
    return None


class Positions(object):
    """The positions of a container while its layout is restored. A position
    holds an object, the UID of an object that cannot be found, or nothing
    """

    def __init__(self, rows, columns):
        self.held = dict(((row, column), None)
                         for row in range(rows) for column in range(columns))

    def holds(self, obj):
        return obj in self.held.values()

    def put(self, obj, row, column):
        """Puts the object at the position, if the container has it and it is
        free. Returns whether the object was put there
        """
        if self.held.get((row, column), False) is not None:
            return False
        self.held[(row, column)] = obj
        return True

    def put_free(self, obj):
        """Puts the object at the first free position and returns it, or None
        if there is no free position left
        """
        free = sorted(pos for pos, held in self.held.items() if held is None)
        if not free:
            return None
        self.held[free[0]] = obj
        return free[0]

    def get_items(self):
        """Returns the occupied positions as a sorted list of (row, column,
        object or UID)
        """
        return sorted((row, column, held)
                      for (row, column), held in self.held.items()
                      if held is not None)


def to_uids(items):
    """Returns the items (row, column, object or UID) with UIDs only, sorted
    """
    def get_uid(obj):
        return obj if api.is_string(obj) else api.get_uid(obj)
    return sorted((row, column, get_uid(obj)) for row, column, obj in items)


def restore_migrated_layout(container, stored, original_ids):
    """Restores the dimensions and layout of a migrated container

    Only the containers the former migration damaged are restored: samples
    containers with their rows and columns swapped, and storage containers
    left with a single position or without the containers they held in AT.
    What cannot take its former position, or has no known one, takes the
    first free position. The restore is recorded in the audit log of the
    container, with what has to be checked by hand.
    """
    attributes = get_migrated_attributes(container)
    rows = api.to_int(attributes.get("Rows"), default=0)
    columns = api.to_int(attributes.get("Columns"), default=0)
    if rows < 1 or columns < 1:
        # not migrated from AT
        return

    path = api.get_path(container)
    is_samples_container = IStorageSamplesContainer.providedBy(container)
    dimensions = (container.getRows(), container.getColumns())
    damaged_dimensions = dimensions != (rows, columns)
    if damaged_dimensions:
        if dimensions != get_migrated_dimensions(container, rows, columns):
            logger.warn("Dimensions of {} changed since the migration "
                        "({}x{}, {}x{} in AT), skipped".format(
                            path, dimensions[0], dimensions[1], rows,
                            columns))
            return
    elif is_samples_container:
        # the migration did not swap the dimensions, so the samples kept
        # their positions
        return

    current_items, missing_items = get_current_items(
        container, original_ids)
    current_objs = [obj for row, column, obj in current_items]
    if is_samples_container:
        stored.difference_update(map(api.get_uid, current_objs))
    at_items = get_at_items(container, attributes, stored, original_ids)

    # A storage container that kept its dimensions is damaged when the
    # containers it held in AT are missing in its layout, or its layout
    # refers to them by a former UID
    layout_uids = [uid for row, column, uid
                   in get_occupied(container.getPositionsLayout())]
    former_uids = [obj for obj in current_objs
                   if api.get_uid(obj) not in layout_uids]
    if not damaged_dimensions and not former_uids and all(
            obj in current_objs for row, column, obj in at_items):
        if is_samples_container or not missing_items:
            return

    positions = Positions(rows, columns)

    # Positions that refer to objects that cannot be found are kept as they
    # are, as long as the container still has them: what they hold is unknown
    lost = []
    for row, column, uid in missing_items:
        if not is_samples_container:
            # A storage container holds containers only, and all of them are
            # known, e.g. the UID is the temporary one of a migrated container
            logger.warn("Position {} of {} refers to the unknown object {}, "
                        "dropped".format((row, column), path, uid))
            continue
        if not positions.put(uid, row, column):
            lost.append((row, column, uid))
            logger.error("Position {} of {} refers to the missing object {} "
                         "and is out of the restored dimensions, check by "
                         "hand".format((row, column), path, uid))

    # The current positions of a samples container are the ones chosen when
    # the samples were stored after the migration. A storage container the
    # migration left with a single position got the containers it holds at
    # the first free one instead, so its AT positions come first
    items = current_items + at_items
    if damaged_dimensions and not is_samples_container:
        items = at_items + current_items

    displaced = []
    for row, column, obj in items:
        if not positions.holds(obj) and not positions.put(obj, row, column):
            displaced.append(obj)
    if not is_samples_container:
        # child containers in no layout
        displaced.extend(get_child_containers(container))

    free_placed = []
    unplaced = []
    for obj in displaced:
        if positions.holds(obj) or obj in unplaced:
            continue
        position = positions.put_free(obj)
        if position is None:
            unplaced.append(obj)
            logger.error("No free position in {} for {}, check by hand"
                         .format(path, api.get_path(obj)))
            continue
        free_placed.append(obj)
        logger.warn("{} placed at the free position {} of {}, check by hand"
                    .format(api.get_path(obj), position, path))

    # compared with the UIDs of the layout, as a former UID of a child
    # resolved above has to be replaced
    occupied = positions.get_items()
    current = sorted(get_occupied(container.getPositionsLayout()))
    if not damaged_dimensions and to_uids(occupied) == current:
        return

    container.rows = rows
    container.columns = columns
    write_layout(container, occupied)
    if damaged_dimensions:
        logger.info("Dimensions of {} restored to {}x{}"
                    .format(path, rows, columns))

    if is_samples_container:
        samples = [obj for row, column, obj in occupied
                   if not api.is_string(obj)]
        stored.update(map(api.get_uid, samples))
        # The samples put back show their container in the samples listing.
        # Their metadata is computed from the storage catalog, so the
        # reindex of the container must be done before theirs
        processQueue()
        for sample in samples:
            if sample not in current_objs:
                sample.reindexObject(idxs=["getDateStored"])

    # record the restore in the audit log of the container
    if snapshot_api.supports_snapshots(container):
        comments = get_restore_comments(
            container, free_placed, unplaced, lost)
        snapshot_api.take_snapshot(container, action="edit",
                                   comments=comments)
        reindex_auditlog(container)


def write_layout(container, occupied):
    """Writes the layout of the container with the occupied positions given
    as a list of (row, column, object or UID of a missing object)
    """
    held = dict(((row, column), obj) for row, column, obj in occupied)
    layout = []
    for row in range(container.getRows()):
        for column in range(container.getColumns()):
            item = container.get_default_layout_item(row, column)
            obj = held.get((row, column))
            if api.is_string(obj):
                # missing object, kept with the default capacity
                item["uid"] = obj
            elif obj is not None:
                capacity = utilization = 1
                if IStorageLayoutContainer.providedBy(obj):
                    capacity = obj.get_samples_capacity()
                    utilization = obj.get_samples_utilization()
                item.update({
                    "uid": api.get_uid(obj),
                    "samples_capacity": capacity,
                    "samples_utilization": utilization,
                })
            layout.append(item)

    # bypass the setter, it notifies the parent before it is restored
    container.positions_layout = layout
    container.rebuild_layout()
    container.reindexObject()
    container.notify_parent()


def get_restore_comments(container, free_placed, unplaced, lost):
    """Returns the comments for the audit log entry of the restore
    """
    comments = "Layout restored after the migration to Dexterity"
    if free_placed:
        comments += ". Placed at a free position, check by hand: {}".format(
            ", ".join(map(api.get_id, free_placed)))
    if unplaced:
        comments += ". No free position, check by hand: {}".format(
            ", ".join(map(api.get_id, unplaced)))
    if lost:
        comments += ". Positions of missing objects out of the restored " \
            "dimensions, check by hand: {}".format(", ".join(
                "{} at {}".format(uid, container.position_to_alpha(
                    row, column)) for row, column, uid in lost))
    return comments
