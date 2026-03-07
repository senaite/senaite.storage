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
from plone import api as ploneapi
from senaite.core import permissions
from Products.CMFCore import permissions as cmf_permissions
from senaite.core.api.workflow import update_workflow
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.setuphandlers import setup_catalog_mappings
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.setuphandlers import setup_other_catalogs
from senaite.core.workflow import SAMPLE_WORKFLOW
from senaite.storage import logger
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.catalog import StorageCatalog
from senaite.storage.config import PRODUCT_NAME
from senaite.storage.config import PROFILE_ID

SITE_STRUCTURE = [
    # Tuples of (portal_type, obj_id, obj_title, parent_path, display_type)
    # If parent_path is None, assume folder_id is portal
    ("StorageRootFolder", "senaite_storage", "Sample storage", None, True)
]

ID_FORMATTING = [
    # An array of dicts. Each dict represents an ID formatting configuration
    {
        "portal_type": "StorageFacility",
        "form": "SF-{seq:05d}",
        "prefix": "sstoragefacility",
        "sequence_type": "generated",
        "counter_type": "",
        "split_length": 1,
    }, {
        "portal_type": "StoragePosition",
        "form": "SP-{seq:05d}",
        "prefix": "sstorageposition",
        "sequence_type": "generated",
        "counter_type": "",
        "split_length": 1,
    }, {
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

CATALOGS = (
    StorageCatalog,
)

# Tuples of (type, [catalog])
CATALOG_MAPPINGS = [
]

# Tuples of (catalog, index_name, index_attribute, index_type)
INDEXES = [
    # Index used in ARs view to sort items by date stored by default
    (SAMPLE_CATALOG, "getDateStored", "", "DateIndex"),
    (SAMPLE_CATALOG, "getStorageExpiryDate", "", "DateIndex"),
]

# Tuples of (catalog, column name)
COLUMNS = [
    # To display the column Date Stored in AR listings
    (SAMPLE_CATALOG, "getDateStored"),
    # To display the Container where the Sample is located in listings
    (SAMPLE_CATALOG, "getSamplesContainerURL"),
    (SAMPLE_CATALOG, "getSamplesContainerID")
]

WORKFLOWS_TO_UPDATE = {
    SAMPLE_WORKFLOW: {
        "states": {
            "sample_received": {
                # Use a list to extend transitions
                "transitions": ["store"],
            },
            "to_be_verified": {
                # Use a list to extend transitions
                "transitions": ["store"],
            },
            "verified": {
                # Use a list to extend transitions
                "transitions": ["store"],
            },
            "published": {
                # Use a list to extend transitions
                "transitions": ["store"],
            },
            "stored": {
                "title": "Stored",
                "description": "Sample is stored",
                "transitions": ("recover", "detach", "dispatch", ),
                # Copy permissions from sample_received first
                "permissions_copy_from": "sample_received",
                # Override permissions
                "permissions": {
                    # **Add** (acquire=True) storage-specific roles
                    cmf_permissions.View: [
                        "StorageManager", "StorageAssistant"
                    ],
                    cmf_permissions.AccessContentsInformation: [
                        "StorageManager", "StorageAssistant"
                    ],
                    cmf_permissions.ListFolderContents: [
                        "StorageManager", "StorageAssistant"
                    ],
                    # Note here we are passing tuples, so these permissions are
                    # set with acquire=False
                    cmf_permissions.ModifyPortalContent: (),
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
            },
        },
        "transitions": {
            "store": {
                "title": "Store",
                "new_state": "stored",
                "action": "Store sample",
                "guard": {
                    "guard_permissions": "senaite.storage: Transition: Store Sample",  # noqa
                    "guard_roles": "",
                    "guard_expr": "python:here.guard_handler('store')",
                }
            },
            "recover": {
                "title": "Recover",
                # We set same new_state here because system will transition the
                # sample to the state before when was stored. See events
                "new_state": "stored",
                "action": "Recover sample",
                "guard": {
                    "guard_permissions": "senaite.storage: Transition: Recover Sample",  # noqa
                    "guard_roles": "",
                    "guard_expr": "python:here.guard_handler('recover')",
                }
            },
        }
    }
}
ROLES = [
    # Tuple of (role, [permissions])
    #
    # Permission assignment strategy for this add-on:
    #
    # 1. Portal-level permissions (site root):
    #
    #    - OUR permissions → roles: use `rolemap.xml`
    #    - OTHER add-ons' permissions → OUR roles: use `setup_roles()` below
    #
    #    Why not use rolemap.xml for both? Because rolemap.xml replaces the
    #    entire role list for a permission, even with acquire="1". This would
    #    remove roles that other add-ons have already assigned.
    #
    # 2. Content-level permissions (objects managed by workflows):
    #
    #    - OUR content types: defined in our DC workflow definitions
    #    - OTHER add-ons' content types: use WORKFLOWS_TO_UPDATE above
    #
    ("StorageManager", [
        cmf_permissions.View,
        cmf_permissions.AccessContentsInformation,
        cmf_permissions.ListFolderContents,
        # core's `ManageAnalysisRequests` permission is required for:
        #
        #   - AnalysisRequest's `base_view` and its analyses tables
        #     See https://github.com/senaite/senaite.core/blob/a8cbc4546/src/bika/lims/browser/analysisrequest/configure.zcml#L80-L114
        #
        #   - The `storage_store_samples` view (container assignment to
        #     pre-selected samples) and `storage_store_container` view (samples
        #     assignment to a pre-selected container)
        #     See browser/container/configure.zcml
        permissions.ManageAnalysisRequests,
    ]),
    ("StorageAssistant", [
        cmf_permissions.View,
        cmf_permissions.AccessContentsInformation,
        cmf_permissions.ListFolderContents,
        permissions.ManageAnalysisRequests,
    ]),
]

GROUPS = [
    # Tuple of (group_name, [roles])
    ("Storage Managers", ["Member", "StorageManager"], ),
    ("Storage Assistants", ["Member", "StorageAssistant"], ),
]


def pre_install(portal_setup):
    """Runs before the first import step of the *default* profile
    This handler is registered as a *pre_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} pre-install handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_ID)
    portal = context.getSite()  # noqa

    # Only install senaite.lims once!
    qi = portal.portal_quickinstaller
    if not qi.isProductInstalled("senaite.lims"):
        portal_setup.runAllImportStepsFromProfile(
            "profile-senaite.lims:default")

    logger.info("{} pre-install handler [DONE]".format(PRODUCT_NAME.upper()))


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

    # Setup roles permissions for portal
    setup_roles(portal)

    # Setup user groups
    setup_user_groups(portal)

    # Setup site structure
    setup_site_structure(portal)

    # Setup ID Formatting for Storage content types
    setup_id_formatting(portal)

    # Injects "store" and "recover" transitions into senaite's workflow
    setup_workflows(portal)

    # reindex storage structure
    # needed when uninstalled/reinstalled
    reindex_storage_structure(portal)

    logger.info("{} install handler [DONE]".format(PRODUCT_NAME.upper()))


def post_uninstall(portal_setup):
    """Runs after the last import step of the *uninstall* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} uninstall handler [BEGIN]".format(PRODUCT_NAME.upper()))

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = "profile-{}:uninstall".format(PRODUCT_NAME)
    context = portal_setup._getImportContext(profile_id)  # noqa
    portal = context.getSite()  # noqa

    # recover all stored samples
    recover_samples(portal)

    # unindex the storage structure
    # -> makes it disappear in the navigation
    unindex_storage_structure(portal)

    # uninstall storage workflow settings
    uninstall_workflows(portal)

    # uninstall storage catalog
    uninstall_storage_catalog(portal)

    logger.info("{} uninstall handler [DONE]".format(PRODUCT_NAME.upper()))


def setup_catalogs(portal):
    """Setup storage catalogs
    """
    setup_core_catalogs(portal, catalog_classes=CATALOGS)
    setup_other_catalogs(portal, indexes=INDEXES, columns=COLUMNS)
    setup_catalog_mappings(portal, catalog_mappings=CATALOG_MAPPINGS)


def setup_roles(portal):
    """Setup the top-level permissions (at portal) for product-specific roles.
    The roles are added for each permission in portal root while keeping the
    existing acquire setting
    """
    logger.info("Setup storage-specific roles ...")

    # Default permissions
    for role_name, perms in ROLES:
        for permission in perms:
            grant_permission_to(portal, permission, role_name)

    logger.info("Setup storage-specific roles [DONE]")


def grant_permission_to(folder, permission, role):
    """Grants a permission to the given role and given folder
    :param folder: the folder to which the permission for the role must apply
    :param permission: the permission to be assigned
    :param role: role to which the permission must be granted
    :return True if succeeded, otherwise, False
    """
    roles = filter(lambda perm: perm.get("selected") == "SELECTED",
                   folder.rolesOfPermission(permission))
    roles = map(lambda perm_role: perm_role["name"], roles)
    if role in roles:
        # Nothing to do, the role has the permission granted already
        logger.info("Role '{}' has permission {} for {} already".format(
            role, repr(permission), repr(folder)))
        return False

    roles.append(role)
    acquire = folder.acquiredRolesAreUsedBy(permission) == "CHECKED" and 1 or 0
    folder.manage_permission(permission, roles=roles, acquire=acquire)
    folder.reindexObject()
    logger.info("Added permission {} to role '{}' for {}".format(
        repr(permission), role, repr(folder)))

    return True


def setup_user_groups(portal):
    """Configure the product-specific user groups
    """
    logger.info("Setup storage-specific user groups ...")
    groups = portal.portal_groups
    existing = groups.listGroupIds()

    for group, roles in GROUPS:
        if group in existing:
            # group exists already, grant default roles
            logger.info("Group '%s' already exists. Granted roles: %s" %
                        (group, ", ".join(roles)))
            ploneapi.group.grant_roles(groupname=group, roles=roles)
            break

        # group does not exist yet
        logger.info("Group '%s' added. Granted roles: %s" %
                    (group, ", ".join(roles)))
        groups.addGroup(group, title=group, roles=roles)

    logger.info("Setup storage-specific user groups [DONE]")


def setup_workflows(portal):
    """Injects 'store' and 'recover' transitions into workflow
    """
    logger.info("Setup storage workflow ...")
    for wf_id, settings in WORKFLOWS_TO_UPDATE.items():
        update_workflow(wf_id, **settings)
    logger.info("Setup storage workflow [DONE]")


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


def setup_site_structure(portal):
    """Setup contents structure for senaite.storage
    """
    logger.info("Setup site structure ...")

    def resolve_parent(parent_path):
        if not parent_path:
            return portal
        return api.get_object_by_path(parent_path, default=None)

    for portal_type, obj_id, obj_title, parent_path, display in SITE_STRUCTURE:
        parent = resolve_parent(parent_path)
        if not parent:
            logger.warn("Parent path {} does not exist".format(parent_path))
            continue

        if obj_id in parent:
            logger.info("Object {}/{} already exists"
                        .format(api.get_path(parent), obj_id))
            obj = parent._getOb(obj_id)
        else:
            obj = api.create(parent, portal_type, id=obj_id, title=obj_title)

        if display:
            # Display the object in the nav bar
            display_in_nav(obj)

    logger.info("Setup site structure [DONE]")


def display_in_nav(obj):
    """Makes an object and/or objects from the given portal type to be
    displayed in the navigation bar
    """
    portal_type = api.get_portal_type(obj)

    # remove from senaite setup's sidebar_skip_types
    setup = api.get_senaite_setup()
    skip = setup.getSidebarSkipTypes()
    if skip and portal_type in skip:
        skip = tuple(pt for pt in skip if pt != portal_type)
        setup.setSidebarSkipTypes(skip)

    # if a root folder, add to senaite setup's sidebar_folders
    setup = api.get_senaite_setup()
    portal = api.get_portal()
    if api.get_parent(obj) == portal:
        obj_id = api.get_id(obj)
        folders = setup.getSidebarFolders()
        if obj_id not in folders:
            folders += (obj_id, )
            setup.setSidebarFolders(folders)

def reindex_storage_structure(portal):
    """Reindex storage structure
    """
    logger.info("*** Reindex storage structure ***")

    def reindex(obj, recurse=False):
        # skip catalog tools etc.
        if api.is_object(obj):
            logger.info("Reindexing {}".format(repr(obj)))
            obj.reindexObject()
        if recurse and hasattr(aq_base(obj), "objectValues"):
            map(lambda o: reindex(o, recurse=recurse),
                obj.objectValues())

    storage = portal.senaite_storage

    for obj in storage.objectValues():
        reindex(obj, recurse=True)

    storage.reindexObject()


def unindex_storage_structure(portal):
    """Unindex storage structure
    """
    logger.info("*** Unindex storage structure ***")

    def unindex(obj, recurse=False):
        # skip catalog tools etc.
        if api.is_object(obj):
            logger.info("Unindexing {}".format(repr(obj)))
            obj.unindexObject()
        if recurse and hasattr(aq_base(obj), "objectValues"):
            map(lambda o: unindex(o, recurse=recurse),
                obj.objectValues())

    storage = portal.senaite_storage

    for obj in storage.objectValues():
        unindex(obj, recurse=True)

    storage.unindexObject()


def recover_samples(portal):
    """recover all stored samples
    """
    logger.info("*** Recovering all stored samples ***")
    catalog = api.get_tool(SAMPLE_CATALOG)
    query = {"review_state": "stored"}
    brains = catalog(query)
    total = len(brains)
    logger.info("Recovering {} samples ... ".format(total))
    for num, brain in enumerate(brains):
        obj = api.get_object(brain)
        api.do_transition_for(obj, "recover")
        logger.info("Recovering sample {}/{}: {}".format(
            num + 1, total, api.get_id(obj)))


def uninstall_workflows(portal):
    """Uninstall injected WFs
    """
    logger.info("*** Uninstall storage workflows ...")
    wf_tool = api.get_tool("portal_workflow")

    workflow = wf_tool.getWorkflowById(SAMPLE_WORKFLOW)
    states = workflow.states

    DELETE_STATES = ["stored"]
    DELETE_TRANSITIONS = ["store", "recover"]

    for sid, state in states.items():
        if sid in DELETE_STATES:
            states.deleteStates([sid])
            logger.info("Deleted state '{}' from workflow '{}'".format(
                sid, workflow.getId()))
            continue
        transitions = filter(
            lambda t: t not in DELETE_TRANSITIONS, state.transitions)
        state.transitions = tuple(transitions)


def uninstall_storage_catalog(portal):
    """Uninstall storage catalog
    """
    logger.info("*** Uninstall storage catalog ...")
    if STORAGE_CATALOG in portal.objectIds():
        portal.manage_delObjects([STORAGE_CATALOG])
