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

    >>> from bika.lims import api
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Functional Helpers:

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
