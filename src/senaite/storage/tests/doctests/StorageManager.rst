StorageManager Role
-------------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t StorageManager

Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> storage = portal.senaite_storage

Set the test user with `StorageManager` role:

    >>> setRoles(portal, TEST_USER_ID, ["StorageManager"])


StorageManager can create facilities
....................................

The storage root folder (`senaite_storage`) allows users with `StorageManager`
role to create `StorageFacility` objects inside it.

    >>> facility = api.create(storage, "StorageFacility", title="Test Facility")
    >>> facility
    <StorageFacility at /plone/senaite_storage/SF-00001>

    >>> facility.Title()
    'Test Facility'

Verify the facility was created in the correct location:

    >>> facility.aq_parent == storage
    True

    >>> "/".join(facility.getPhysicalPath())
    '/plone/senaite_storage/SF-00001'


StorageManager can edit facilities
..................................

StorageManager can modify facility properties:

    >>> facility.setTitle("Updated Facility Name")
    >>> facility.Title()
    'Updated Facility Name'


StorageManager can deactivate and activate facilities
.....................................................

Check the allowed transitions for the facility:

    >>> getAllowedTransitions(facility)
    ['deactivate']

StorageManager can deactivate a facility:

    >>> transitioned = do_action_for(facility, "deactivate")
    >>> api.get_workflow_status_of(facility)
    'inactive'

And activate it again:

    >>> getAllowedTransitions(facility)
    ['activate']

    >>> transitioned = do_action_for(facility, "activate")
    >>> api.get_workflow_status_of(facility)
    'active'


StorageManager can create positions inside facilities
.....................................................

StorageManager can create `StoragePosition` objects inside a facility:

    >>> position = api.create(facility, "StoragePosition", title="Room A")
    >>> position
    <StoragePosition at /plone/senaite_storage/SF-00001/SP-00001>

    >>> position.Title()
    'Room A'

    >>> position.aq_parent == facility
    True


StorageManager can edit positions
.................................

StorageManager can modify position properties:

    >>> position.setTitle("Cold Room A")
    >>> position.Title()
    'Cold Room A'


StorageManager can deactivate and activate positions
....................................................

Check the allowed transitions for the position:

    >>> getAllowedTransitions(position)
    ['deactivate']

StorageManager can deactivate a position:

    >>> transitioned = do_action_for(position, "deactivate")
    >>> api.get_workflow_status_of(position)
    'inactive'

And activate it again:

    >>> getAllowedTransitions(position)
    ['activate']

    >>> transitioned = do_action_for(position, "activate")
    >>> api.get_workflow_status_of(position)
    'active'


StorageManager can create containers
....................................

StorageManager can create `StorageContainer` objects inside a position:

    >>> container = api.create(position, "StorageContainer", title="Freezer A")
    >>> container
    <StorageContainer at /plone/senaite_storage/SF-00001/SP-00001/SC-00001>

    >>> container.Title()
    'Freezer A'

    >>> container.aq_parent == position
    True

StorageManager can also create containers inside other containers (nested):

    >>> nested_container = api.create(container, "StorageContainer", title="Shelf 1")
    >>> nested_container
    <StorageContainer at /plone/senaite_storage/SF-00001/SP-00001/SC-00001/SC-00002>

    >>> nested_container.Title()
    'Shelf 1'

    >>> nested_container.aq_parent == container
    True


StorageManager can edit containers
..................................

StorageManager can modify container properties:

    >>> container.setTitle("Freezer A-1")
    >>> container.Title()
    'Freezer A-1'

    >>> nested_container.setTitle("Shelf 1-A")
    >>> nested_container.Title()
    'Shelf 1-A'


StorageManager can deactivate and activate containers
.....................................................

Check the allowed transitions for the container:

    >>> "deactivate" in getAllowedTransitions(container)
    True

StorageManager can deactivate a container:

    >>> transitioned = do_action_for(container, "deactivate")
    >>> api.get_workflow_status_of(container)
    'inactive'

Deactivating a container also deactivates nested containers:

    >>> api.get_workflow_status_of(nested_container)
    'inactive'

And activate it again:

    >>> "activate" in getAllowedTransitions(container)
    True

    >>> transitioned = do_action_for(container, "activate")
    >>> api.get_workflow_status_of(container)
    'active'

Activating a container also activates nested containers:

    >>> api.get_workflow_status_of(nested_container)
    'active'


StorageManager can create samples containers
............................................

StorageManager can create `StorageSamplesContainer` objects inside a container:

    >>> samples_container = api.create(container, "StorageSamplesContainer", title="Box A", Rows=3, Columns=3)
    >>> samples_container
    <StorageSamplesContainer at /plone/senaite_storage/SF-00001/SP-00001/SC-00001/SS-00001>

    >>> samples_container.Title()
    'Box A'

    >>> samples_container.aq_parent == container
    True

    >>> samples_container.getRows()
    3

    >>> samples_container.getColumns()
    3

    >>> samples_container.get_samples_capacity()
    9


StorageManager can edit samples containers
..........................................

StorageManager can modify samples container properties:

    >>> samples_container.setTitle("Box A-1")
    >>> samples_container.Title()
    'Box A-1'


StorageManager can deactivate and activate samples containers
.............................................................

Check the allowed transitions for the samples container:

    >>> "deactivate" in getAllowedTransitions(samples_container)
    True

StorageManager can deactivate a samples container:

    >>> transitioned = do_action_for(samples_container, "deactivate")
    >>> api.get_workflow_status_of(samples_container)
    'inactive'

And activate it again:

    >>> "activate" in getAllowedTransitions(samples_container)
    True

    >>> transitioned = do_action_for(samples_container, "activate")
    >>> api.get_workflow_status_of(samples_container)
    'active'


StorageManager can create full storage hierarchy
................................................

Create a complete storage hierarchy:

    >>> facility2 = api.create(storage, "StorageFacility", title="Main Storage")
    >>> facility2
    <StorageFacility at /plone/senaite_storage/SF-00002>

    >>> position2 = api.create(facility2, "StoragePosition", title="Room B")
    >>> position2
    <StoragePosition at /plone/senaite_storage/SF-00002/SP-00002>

    >>> container2 = api.create(position2, "StorageContainer", title="Freezer 1")
    >>> container2
    <StorageContainer at /plone/senaite_storage/SF-00002/SP-00002/SC-00003>

    >>> samples_container2 = api.create(container2, "StorageSamplesContainer", title="Box 1", Rows=3, Columns=3)
    >>> samples_container2
    <StorageSamplesContainer at /plone/senaite_storage/SF-00002/SP-00002/SC-00003/SS-00002>
