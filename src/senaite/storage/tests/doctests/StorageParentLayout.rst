Storage Parent Layout
---------------------

A storage container that holds other containers keeps, for each of them, the
position where it is stored and its samples capacity and utilization, so it
can tell how many samples it can store in total. A container is added to the
layout of its parent container as soon as it is created, however it is
created, and the parent learns about any later change of its dimensions.

Test Setup
..........

Running this test from the buildout directory:

    bin/test -t StorageParentLayout

Needed Imports:

    >>> import transaction
    >>> from bika.lims import api
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Functional Helpers:

    >>> def get_items(parent, child):
    ...     uid = api.get_uid(child)
    ...     items = parent.getPositionsLayout()
    ...     return [item for item in items if item.get("uid") == uid]

    >>> def get_item(parent, child):
    ...     uid = api.get_uid(child)
    ...     items = parent.getPositionsLayout()
    ...     return [item for item in items if item.get("uid") == uid][0]

Variables:

    >>> portal = self.portal
    >>> storage = portal.senaite_storage

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager", ])

Setup baseline storage objects for the test, with a freezer of 3 x 3
positions:

    >>> sf = api.create(storage, "StorageFacility", title="Storage facility")
    >>> sp = api.create(sf, "StoragePosition", title="Room A")
    >>> freezer = api.create(sp, "StorageContainer", title="Freezer A",
    ...                      rows=3, columns=3)
    >>> len(freezer.getPositionsLayout())
    9


Container created with its dimensions
.....................................

`api.create` adds the container before it sets its fields. Still, the box is
added to the freezer with its full capacity:

    >>> box = api.create(freezer, "StorageSamplesContainer", title="Box A",
    ...                  rows=2, columns=5)
    >>> box.get_samples_capacity()
    10
    >>> freezer.has_object(box)
    True
    >>> get_item(freezer, box)["samples_capacity"]
    10


Dimensions set after the creation
.................................

The JSON API creates the container first, and then sets the submitted fields
through their setters, without a modified event. The freezer learns about the
capacity of the box all the same:

    >>> box = api.create(freezer, "StorageSamplesContainer", title="Box B")
    >>> box.setRows(2)
    >>> box.setColumns(5)
    >>> freezer.has_object(box)
    True
    >>> get_item(freezer, box)["samples_capacity"]
    10


Dimensions changed
..................

When the dimensions of a stored container change, its parent updates the
capacity it keeps, and the container stays at its position:

    >>> position = freezer.get_object_position(box)
    >>> box.setRows(4)
    >>> get_item(freezer, box)["samples_capacity"]
    20
    >>> freezer.get_object_position(box) == position
    True


Nested containers
.................

The capacity of a box reaches the freezer through the rack that stores it:

    >>> rack = api.create(freezer, "StorageContainer", title="Rack A",
    ...                   rows=1, columns=2)
    >>> box = api.create(rack, "StorageSamplesContainer", title="Box C",
    ...                  rows=2, columns=5)
    >>> rack.has_object(box)
    True
    >>> freezer.has_object(rack)
    True
    >>> rack.get_samples_capacity()
    11
    >>> get_item(freezer, rack)["samples_capacity"]
    11


Moved containers
................

A container moved to another one, as the "Move container" view does, leaves
the layout of its former parent and takes the first free position of the new
one. Both update the capacity they keep:

    >>> freezer_b = api.create(sp, "StorageContainer", title="Freezer B",
    ...                        rows=2, columns=2)
    >>> box = api.move_object(box, freezer_b, check_constraints=False)
    >>> rack.has_object(box), freezer_b.has_object(box)
    (False, True)
    >>> freezer_b.get_object_position(box)
    (0, 0)
    >>> get_item(freezer_b, box)["samples_capacity"]
    10
    >>> rack.get_samples_capacity()
    2
    >>> get_item(freezer, rack)["samples_capacity"]
    2

A container moved out of a container to a storage position leaves the layout
of the former, and the one moved into a container from a storage position
takes its first free position:

    >>> rack = api.move_object(rack, sp, check_constraints=False)
    >>> freezer.has_object(rack)
    False
    >>> rack = api.move_object(rack, freezer_b, check_constraints=False)
    >>> freezer_b.has_object(rack)
    True
    >>> freezer_b.get_object_position(rack)
    (0, 1)

A container renamed in its parent keeps its position:

    >>> position = freezer_b.get_object_position(box)
    >>> _ = transaction.savepoint(optimistic=True)
    >>> freezer_b.manage_renameObject(box.getId(), "box-c")
    >>> box = freezer_b["box-c"]
    >>> freezer_b.get_object_position(box) == position
    True
    >>> len(get_items(freezer_b, box))
    1

A container moved into a container with no free position leaves the layout of
its former parent all the same. The new one does not have it in its layout:

    >>> full = api.create(sp, "StorageContainer", title="Full", rows=1,
    ...                   columns=1)
    >>> api.create(full, "StorageContainer", title="Only")
    <StorageContainer at ...>
    >>> box = api.move_object(box, full, check_constraints=False)
    >>> freezer_b.has_object(box), full.has_object(box)
    (False, False)

The contents of an AT container are only moved by the migration to Dexterity,
which keeps the layouts itself, so its layout is left as it is:

    >>> from senaite.storage.content.storagecontainer import \
    ...     StorageContainer as ATStorageContainer
    >>> sp._setObject("at-rack", ATStorageContainer("at-rack"))
    'at-rack'
    >>> at_rack = sp._getOb("at-rack")
    >>> at_rack.setRows(1)
    >>> at_rack.setColumns(2)
    >>> shelf = api.create(sp, "StorageContainer", title="Shelf")
    >>> shelf = api.move_object(shelf, at_rack, check_constraints=False)
    >>> at_rack.has_object(shelf)
    True
    >>> shelf = api.move_object(shelf, sp, check_constraints=False)
    >>> at_rack.has_object(shelf)
    True
