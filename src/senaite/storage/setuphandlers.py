# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from bika.lims import api
from senaite.storage import PRODUCT_NAME
from senaite.storage import PROFILE_ID
from senaite.storage import logger

ACTIONS_TO_HIDE = [
    # Tuples of (id, folder_id)
    # If folder_id is None, assume folder_id is portal
    ("bika_storagelocations", "bika_setup")
]

NEW_CONTENT_TYPES = [
    # Tuples of (id, folder_id)
    # If folder_id is None, assume folder_id is portal
    ("senaite_storage", None),
]

CATALOGS_BY_TYPE = [
    # Tuples of (type, [catalog])
    ("StorageContainer", ["senaite_storage_catalog"]),
    ("StorageFacility", ["senaite_storage_catalog"]),
    ("StorageRootFolder", ["senaite_storage_catalog"]),
    ("StorageSamplesContainer", ["senaite_storage_catalog"]),
]

INDEXES = [
    # Tuples of (catalog, id, indexed attribute, type)
]

COLUMNS = [
    # Tuples of (catalog, column name)
]


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} install handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_ID)
    portal = context.getSite()  # noqa

    # Setup catalogs
    #setup_catalogs(portal)

    # Reindex new content types
    reindex_new_content_types(portal)

    # Hide actions
    hide_actions(portal)

    # Migrate "classic" storage locations
    migrate_storage_locations(portal)

    logger.info("{} install handler [DONE]".format(PRODUCT_NAME.upper()))


def setup_catalogs(portal):
    """Setup Plone catalogs
    """
    logger.info("Setup Catalogs ...")

    # Setup catalogs by type
    for type_name, catalogs in CATALOGS_BY_TYPE:
        at = api.get_tool("archetype_tool")
        # get the current registered catalogs
        current_catalogs = at.getCatalogsByType(type_name)
        # get the desired catalogs this type should be in
        desired_catalogs = map(api.get_tool, catalogs)
        # check if the catalogs changed for this portal_type
        if set(current_catalogs).difference(desired_catalogs):
            # fetch the brains to reindex
            brains = api.search({"portal_type": type_name})
            # updated the catalogs
            at.setCatalogsByType(type_name, catalogs)
            logger.info("Assign '%s' type to Catalogs %s" %
                        (type_name, catalogs))
            for brain in brains:
                obj = api.get_object(brain)
                logger.info("Reindexing '%s'" % repr(obj))
                obj.reindexObject()

    # Setup catalog indexes
    to_index = []
    for catalog, name, attribute, meta_type in INDEXES:
        c = api.get_tool(catalog)
        indexes = c.indexes()
        if name in indexes:
            logger.info("Index '%s' already in Catalog [SKIP]" % name)
            continue

        logger.info("Adding Index '%s' for field '%s' to catalog ..."
                    % (meta_type, name))
        c.addIndex(name, meta_type)
        to_index.append((c, name))
        logger.info("Added Index '%s' for field '%s' to catalog [DONE]"
                    % (meta_type, name))

    for catalog, name in to_index:
        logger.info("Indexing new index '%s' ..." % name)
        catalog.manage_reindexIndex(name)
        logger.info("Indexing new index '%s' [DONE]" % name)

    # Setup catalog metadata columns
    for catalog, name in COLUMNS:
        c = api.get_tool(catalog)
        if name not in c.schema():
            logger.info("Adding Column '%s' to catalog '%s' ..."
                        % (name, catalog))
            c.addColumn(name)
            logger.info("Added Column '%s' to catalog '%s' [DONE]"
                        % (name, catalog))
        else:
            logger.info("Column '%s' already in catalog '%s'  [SKIP]"
                        % (name, catalog))
            continue


def reindex_new_content_types(portal):
    """Setup new content types"""
    logger.info("*** Reindex new content types ***")

    def reindex_content_type(obj_id, folder):
        logger.info("Reindexing {}".format(obj_id))
        obj = folder[obj_id]
        obj.unmarkCreationFlag()
        obj.reindexObject()

    # Index objects - Importing through GenericSetup doesn't
    for obj_id, folder_id in NEW_CONTENT_TYPES:
        folder = folder_id and portal[folder_id] or portal
        reindex_content_type(obj_id, folder)


def hide_actions(portal):
    """Excludes actions from both navigation portlet and from control_panel
    """
    logger.info("Hiding actions ...")
    for action_id, folder_id in ACTIONS_TO_HIDE:
        if folder_id and folder_id not in portal:
            logger.info("{} not found in portal [SKIP]".format(folder_id))
            continue
        folder = folder_id and portal[folder_id] or portal
        hide_action(folder, action_id)


def hide_action(folder, action_id):
    logger.info("Hiding {} from {} ...".format(action_id, folder.id))
    if action_id not in folder:
        logger.info("{} not found in {} [SKIP]".format(action_id, folder.id))
        return

    item = folder[action_id]
    logger.info("Hide {} ({}) from nav bar".format(action_id, item.Title()))
    item.setExcludeFromNav(True)

    def get_action_index(action_id):
        for n, action in enumerate(cp.listActions()):
            if action.getId() == action_id:
                return n
        return -1

    logger.info("Hide {} from control_panel".format(action_id, item.Title()))
    cp = api.get_tool("portal_controlpanel")
    action_index = get_action_index(action_id)
    if (action_index == -1):
        logger.info("{}  not found in control_panel [SKIP]".format(cp.id))
        return

    actions = cp._cloneActions()
    del actions[action_index]
    cp._actions = tuple(actions)
    cp._p_changed = 1


def migrate_storage_locations(portal):
    """Migrates classic StorageLocation objects to StorageSamplesContainer
    """
    logger.info("Migrating classic Storage Locations ...")
    query = dict(portal_type="StorageLocation")
    brains = api.search(query, "portal_catalog")
    if not brains:
        logger.info("No Storage Locations found [SKIP]")
        return

    total = len(brains)
    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Migrating Storage Locations: {}/{}".format(num, total))
        object = api.get_object(brain)
        # TODO Migrate
