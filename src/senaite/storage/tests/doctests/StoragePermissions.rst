Storage Permissions
-------------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t StoragePermissions

Test Setup
..........

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> storage = portal.senaite_storage

Create test objects as LabManager:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])
    >>> facility = api.create(storage, "StorageFacility", title="Test Facility")
    >>> position = api.create(facility, "StoragePosition", title="Room A")
    >>> container = api.create(position, "StorageContainer", title="Freezer A")
    >>> samples_container = api.create(container, "StorageSamplesContainer", title="Box A", Rows=3, Columns=3)


Storage root folder permissions
...............................

The `Add portal content` permission in the storage root folder is granted to
`StorageManager`:

    >>> "StorageManager" in rolesForPermissionOn("Add portal content", storage)
    True

But `StorageAssistant` cannot add content to the storage root folder:

    >>> "StorageAssistant" in rolesForPermissionOn("Add portal content", storage)
    False

The specific permission for adding facilities is granted to `StorageManager`:

    >>> "StorageManager" in rolesForPermissionOn("senaite.storage: Add Storage Facility", storage)
    True


Facility permissions
....................

Inside a facility, both `StorageManager` and `StorageAssistant` have `Add portal
content` permission (needed for creating positions and containers):

    >>> "StorageManager" in rolesForPermissionOn("Add portal content", facility)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("Add portal content", facility)
    True

Both roles can modify facility content:

    >>> "StorageManager" in rolesForPermissionOn("Modify portal content", facility)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("Modify portal content", facility)
    True

Both roles can view facilities:

    >>> "StorageManager" in rolesForPermissionOn("View", facility)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("View", facility)
    True


Position permissions
....................

Inside a position, both roles have `Add portal content` permission:

    >>> "StorageManager" in rolesForPermissionOn("Add portal content", position)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("Add portal content", position)
    True

Both roles can modify and view positions:

    >>> "StorageManager" in rolesForPermissionOn("Modify portal content", position)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("Modify portal content", position)
    True

    >>> "StorageManager" in rolesForPermissionOn("View", position)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("View", position)
    True


Container permissions
.....................

Inside a container, both roles have `Add portal content` permission:

    >>> "StorageManager" in rolesForPermissionOn("Add portal content", container)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("Add portal content", container)
    True

Both roles can modify and view containers:

    >>> "StorageManager" in rolesForPermissionOn("Modify portal content", container)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("Modify portal content", container)
    True

    >>> "StorageManager" in rolesForPermissionOn("View", container)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("View", container)
    True


Activate/Deactivate transition permissions
..........................................

Only `StorageManager` has the permission to activate and deactivate storage
objects. `StorageAssistant` cannot activate or deactivate.

Deactivate permission:

    >>> "StorageManager" in rolesForPermissionOn("senaite.storage: Transition: Deactivate", facility)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("senaite.storage: Transition: Deactivate", facility)
    False

Activate permission:

    >>> "StorageManager" in rolesForPermissionOn("senaite.storage: Transition: Activate", facility)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("senaite.storage: Transition: Activate", facility)
    False

The same applies to positions:

    >>> "StorageManager" in rolesForPermissionOn("senaite.storage: Transition: Deactivate", position)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("senaite.storage: Transition: Deactivate", position)
    False

And containers:

    >>> "StorageManager" in rolesForPermissionOn("senaite.storage: Transition: Deactivate", container)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("senaite.storage: Transition: Deactivate", container)
    False


Add/Recover Samples transition permissions
..........................................

Both `StorageManager` and `StorageAssistant` can add and recover samples from
storage containers:

    >>> "StorageManager" in rolesForPermissionOn("senaite.storage: Transition: Add Samples", samples_container)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("senaite.storage: Transition: Add Samples", samples_container)
    True

    >>> "StorageManager" in rolesForPermissionOn("senaite.storage: Transition: Recover Samples", samples_container)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("senaite.storage: Transition: Recover Samples", samples_container)
    True


Move Container transition permissions
.....................................

Both `StorageManager` and `StorageAssistant` can move containers:

    >>> "StorageManager" in rolesForPermissionOn("senaite.storage: Transition: Move Container", container)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("senaite.storage: Transition: Move Container", container)
    True

    >>> "StorageManager" in rolesForPermissionOn("senaite.storage: Transition: Move Container", samples_container)
    True

    >>> "StorageAssistant" in rolesForPermissionOn("senaite.storage: Transition: Move Container", samples_container)
    True


StorageAssistant cannot create facilities
.........................................

Users with only `StorageAssistant` role cannot create facilities in the storage
root folder. They can only add content inside existing facilities.

    >>> setRoles(portal, TEST_USER_ID, ["StorageAssistant"])

Attempting to create a facility as StorageAssistant should raise Unauthorized:

    >>> try:
    ...     api.create(storage, "StorageFacility", title="Unauthorized Facility")
    ... except Exception as e:
    ...     print(e.__class__.__name__)
    Unauthorized


StorageAssistant can create positions and containers
....................................................

StorageAssistant can create positions inside facilities:

    >>> new_position = api.create(facility, "StoragePosition", title="Room B")
    >>> new_position.Title()
    'Room B'

StorageAssistant can create containers inside positions:

    >>> new_container = api.create(new_position, "StorageContainer", title="Freezer B")
    >>> new_container.Title()
    'Freezer B'

StorageAssistant can create samples containers inside containers:

    >>> new_samples_container = api.create(new_container, "StorageSamplesContainer", title="Box B", Rows=2, Columns=2)
    >>> new_samples_container.Title()
    'Box B'
