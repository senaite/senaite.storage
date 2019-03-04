# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

import random

from Products.DCWorkflow.Guard import Guard
from bika.lims import api
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog.catalog_utilities import addZCTextIndex
from bika.lims import permissions
from senaite.storage import PRODUCT_NAME
from senaite.storage import PROFILE_ID
from senaite.storage import logger
from senaite.storage.catalog import SENAITE_STORAGE_CATALOG

CREATE_TEST_DATA = True
CREATE_TEST_DATA_RANDOM = False

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

ID_FORMATTING = [
    # An array of dicts. Each dict represents an ID formatting configuration
    {
        "portal_type": "StorageContainer",
        "form": "SC-{seq:05d}",
        "prefix": "sstoragecontainer",
        "sequence_type": "generated",
        "counter_type": "",
        "split_length": 1,
    }, {
        "portal_type": "StorageSamplesContainer",
        "form": "SS-{seq:05d}",
        "prefix": "sstoragesamplescontainer",
        "sequence_type": "generated",
        "counter_type": "",
        "split_length": 1,
    },
]

CATALOGS_BY_TYPE = [
    # Tuples of (type, [catalog])
    ("StorageSamplesContainer", ["portal_catalog", SENAITE_STORAGE_CATALOG]),
]

INDEXES = [
    # Tuples of (catalog, index_name, index_type)
    # This index is required by reference_widget in searches
    (SENAITE_STORAGE_CATALOG, "allowedRolesAndUsers", "KeywordIndex"),
    # Ids of parent containers and current
    (SENAITE_STORAGE_CATALOG, "get_all_ids", "KeywordIndex"),
    # Keeps the sample uids stored in each sample container
    (SENAITE_STORAGE_CATALOG, "get_samples_uids", "KeywordIndex"),
    # For searches, made of get_all_ids + Title
    (SENAITE_STORAGE_CATALOG, "get_searchable_text", "ZCTextIndex"),
    # Index used in searches to filter sample containers with available slots
    (SENAITE_STORAGE_CATALOG, "is_full", "BooleanIndex"),
    (SENAITE_STORAGE_CATALOG, "review_state", "FieldIndex"),
    # Index used in ARs view to sort items by date stored by default
    (CATALOG_ANALYSIS_REQUEST_LISTING, "getDateStored", "DateIndex"),
]

COLUMNS = [
    # Tuples of (catalog, column name)
    (SENAITE_STORAGE_CATALOG, "Title"),
    # To get the UID of the selected container in searches (reference widget)
    (SENAITE_STORAGE_CATALOG, "UID"),
    # To display the column Date Stored in AR listings
    (CATALOG_ANALYSIS_REQUEST_LISTING, "getDateStored"),
    # To display the Container where the Sample is located in listings
    (CATALOG_ANALYSIS_REQUEST_LISTING, "getSamplesContainerURL"),
    (CATALOG_ANALYSIS_REQUEST_LISTING, "getSamplesContainerID")
]

WORKFLOWS_TO_UPDATE = {
    "bika_ar_workflow": {
        "permissions": (),
        "states": {
            "sample_received": {
                # Do not remove transitions already there
                "preserve_transitions": True,
                "transitions": ("store",),
            },
            "stored": {
                "title": "Stored",
                "description": "Sample is stored",
                "transitions": ("recover",),
                # Copy permissions from sample_received first
                "permissions_copy_from": "sample_received",
                # Override permissions
                "permissions": {
                    # Note here we are passing tuples, so these permissions are
                    # set with acquire=False
                    permissions.AddAnalysis: (),
                    permissions.AddAttachment: (),
                    permissions.TransitionCancelAnalysisRequest: (),
                    permissions.TransitionReinstateAnalysisRequest: (),
                    permissions.EditFieldResults: (),
                    permissions.EditResults: (),
                    permissions.TransitionPreserveSample: (),
                    permissions.TransitionPublishResults: (),
                    permissions.TransitionScheduleSampling: (),
                }
            }
        },
        "transitions": {
            "store": {
                "title": "Store",
                "new_state": "stored",
                "action": "Store sample",
                "guard": {
                    "guard_permissions": "",
                    "guard_roles": "",
                    "guard_expr": "",
                }
            },
            "recover": {
                "title": "Recover",
                "new_state": "sample_received",
                "action": "Recover sample",
                "guard": {
                    "guard_permissions": "",
                    "guard_roles": "",
                    "guard_expr": "",
                }
            }
        }
    }
}


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} install handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_ID)
    portal = context.getSite()  # noqa

    # Setup catalogs
    setup_catalogs(portal)

    # Reindex new content types
    reindex_new_content_types(portal)

    # Setup ID Formatting for Storage content types
    setup_id_formatting(portal)

    # Hide actions
    hide_actions(portal)

    # Migrate "classic" storage locations
    migrate_storage_locations(portal)

    # Injects "store" and "recover" transitions into senaite's workflow
    setup_workflows(portal)

    # Create test data
    create_test_data(portal)

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
        if set(desired_catalogs).difference(current_catalogs):
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
    for catalog, name, meta_type in INDEXES:
        c = api.get_tool(catalog)
        indexes = c.indexes()
        if name in indexes:
            logger.info("Index '%s' already in Catalog [SKIP]" % name)
            continue

        logger.info("Adding Index '%s' for field '%s' to catalog '%s"
                    % (meta_type, name, catalog))
        if meta_type == "ZCTextIndex":
            addZCTextIndex(c, name)
        else:
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


def setup_workflows(portal):
    """Injects 'store' and 'recover' transitions into workflow
    """
    logger.info("Setup storage workflow ...")
    for wf_id, settings in WORKFLOWS_TO_UPDATE.items():
        update_workflow(portal, wf_id, settings)


def update_workflow(portal, workflow_id, settings):
    """Injects 'store' and 'recover' transitions into workflow
    """
    logger.info("Updating workflow '{}' ...".format(workflow_id))
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(workflow_id)
    if not workflow:
        logger.warn("Workflow '{}' not found [SKIP]".format(workflow_id))
    states = settings.get("states", {})
    for state_id, values in states.items():
        update_workflow_state(workflow, state_id, values)

    transitions = settings.get("transitions", {})
    for transition_id, values in transitions.items():
        update_workflow_transition(workflow, transition_id, values)


def update_workflow_state(workflow, status_id, settings):
    logger.info("Updating workflow '{}', status: '{}' ..."
                .format(workflow.id, status_id))

    # Create the status (if does not exist yet)
    new_status = workflow.states.get(status_id)
    if not new_status:
        workflow.states.addState(status_id)
        new_status = workflow.states.get(status_id)

    # Set basic info (title, description, etc.)
    new_status.title = settings.get("title", new_status.title)
    new_status.description = settings.get("description", new_status.description)

    # Set transitions
    trans = settings.get("transitions", ())
    if settings.get("preserve_transitions", False):
        trans = tuple(set(new_status.transitions+trans))
    new_status.transitions = trans

    # Set permissions
    update_workflow_state_permissions(workflow, new_status, settings)


def update_workflow_state_permissions(workflow, status, settings):
    # Copy permissions from another state?
    permissions_copy_from = settings.get("permissions_copy_from", None)
    if permissions_copy_from:
        logger.info("Copying permissions from '{}' to '{}' ..."
                    .format(permissions_copy_from, status.id))
        copy_from_state = workflow.states.get(permissions_copy_from)
        if not copy_from_state:
            logger.info("State '{}' not found [SKIP]".format(copy_from_state))
        else:
            for perm_id in copy_from_state.permissions:
                perm_info = copy_from_state.getPermissionInfo(perm_id)
                acquired = perm_info.get("acquired", 1)
                roles = perm_info.get("roles", acquired and [] or ())
                logger.info("Setting permission '{}' (acquired={}): '{}'"
                            .format(perm_id, repr(acquired), ', '.join(roles)))
                status.setPermission(perm_id, acquired, roles)

    # Override permissions
    logger.info("Overriding permissions for '{}' ...".format(status.id))
    state_permissions = settings.get('permissions', {})
    if not state_permissions:
        logger.info(
            "No permissions set for '{}' [SKIP]".format(status.id))
        return
    for permission_id, roles in state_permissions.items():
        state_roles = roles and roles or ()
        if isinstance(state_roles, tuple):
            acq = 0
        else:
            acq = 1
        logger.info("Setting permission '{}' (acquired={}): '{}'"
                    .format(permission_id, repr(acq),
                            ', '.join(state_roles)))
        status.setPermission(permission_id, acq, state_roles)


def update_workflow_transition(workflow, transition_id, settings):
    logger.info("Updating workflow '{}', transition: '{}'"
                .format(workflow.id, transition_id))
    if transition_id not in workflow.transitions:
        workflow.transitions.addTransition(transition_id)
    transition = workflow.transitions.get(transition_id)
    transition.setProperties(
        title=settings.get("title"),
        new_state_id=settings.get("new_state"),
        after_script_name=settings.get("after_script", ""),
        actbox_name=settings.get("action", settings.get("title"))
    )
    guard = transition.guard or Guard()
    guard_props = {"guard_permissions": "",
                   "guard_roles": "",
                   "guard_expr": ""}
    guard_props = settings.get("guard", guard_props)
    guard.changeFromProperties(guard_props)
    transition.guard = guard


def setup_id_formatting(portal, format=None):
    """Setup default ID Formatting for storage content types
    """
    if not format:
        logger.info("Setting up ID formatting ...")
        for formatting in ID_FORMATTING:
            setup_id_formatting(portal, format=formatting)
        return

    bs = portal.bika_setup
    p_type = format.get("portal_type", None)
    if not p_type:
        return
    id_map = bs.getIDFormatting()
    id_format = filter(lambda id: id.get("portal_type", "") == p_type, id_map)
    if id_format:
        logger.info("ID Format for {} already set: '{}' [SKIP]"
                    .format(p_type, id_format[0]["form"]))
        return

    form = format.get("form", "")
    if not form:
        logger.info("Param 'form' for portal type {} not set [SKIP")
        return

    logger.info("Applying format '{}' for {}".format(form, p_type))
    ids = list()
    for record in id_map:
        if record.get('portal_type', '') == p_type:
            continue
        ids.append(record)
    ids.append(format)
    bs.setIDFormatting(ids)


# TODO Remove asap
def create_test_data(portal):
    """Populates with storage-like test data
    """
    if not CREATE_TEST_DATA:
        return
    logger.info("Creating test data ...")
    facilities = portal.senaite_storage
    if len(facilities.objectValues()) > 0:
        logger.info("There are facilities created already [SKIP]")
        return

    def get_random(min, max):
        if not CREATE_TEST_DATA_RANDOM:
            return min
        return int(round(random.uniform(min, max)))

    # Facilities
    for x in range(get_random(3,8)):
        facility = api.create(
            facilities,
            "StorageFacility",
            title="Storage facility {:02d}".format(x+1),
            Phone="123456789",
            EmailAddress="storage{:02d}@example.com".format(x+1),
            PhysicalAddress={
                "address": "Av. Via Augusta 15 - 25",
                "city": "Sant Cugat del Valles",
                "zip": "08174",
                "state": "",
                "country": "Spain",}
        )

        # Fridges
        for i in range(get_random(2,5)):
            container = api.create(facility, "StorageContainer",
                                   title="Fridge {:02d}".format(i+1),
                                   Rows=get_random(4,8),
                                   Columns=get_random(4,6))

            # Racks
            for j in range(get_random(4, container.get_capacity())):
                rack = api.create(container, "StorageContainer",
                                  title="Rack {:02d}".format(j+1),
                                  Rows=get_random(3,4),
                                  Columns=get_random(2,3))

                # Boxes
                for k in range(get_random(2, rack.get_capacity())):
                    box = api.create(rack, "StorageSamplesContainer",
                                     title="Sample box {:02d}".format(k+1),
                                     Rows=get_random(5,10),
                                     Columns=get_random(5,10))
