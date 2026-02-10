StorageAssistant Role
---------------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t StorageAssistant

Test Setup
..........

Needed Imports:

    >>> from AccessControl.unauthorized import Unauthorized
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Functional Helpers:

    >>> def new_sample(services, client, contact, sampletype):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, service_uids)
    ...     return sample

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> storage = portal.senaite_storage


Create base storage structure as LabManager
............................................

StorageAssistant cannot create facilities, so we need to create the base
storage structure first. Set LabManager role:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])

Create a facility:

    >>> facility = api.create(storage, "StorageFacility", title="Test Facility")
    >>> facility
    <StorageFacility at /plone/senaite_storage/SF-00001>

Create base objects for samples:

    >>> client = api.create(portal.clients, "Client", Name="Test Client", ClientID="TC")
    >>> contact = api.create(client, "Contact", Firstname="Test", Lastname="Contact")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> service = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Category=category.UID())


Switch to StorageAssistant role
...............................

Now set StorageAssistant role:

    >>> setRoles(portal, TEST_USER_ID, ["StorageAssistant"])


StorageAssistant CANNOT create facilities
.........................................

StorageAssistant does not have permission to create `StorageFacility` objects
inside the storage root folder:

    >>> try:
    ...     api.create(storage, "StorageFacility", title="Unauthorized Facility")
    ...     raise AssertionError("Should have raised Unauthorized")
    ... except Unauthorized:
    ...     pass


StorageAssistant CAN edit facilities
.....................................

Even though StorageAssistant cannot create facilities, they can edit existing
facilities created by other users:

    >>> facility.setTitle("Updated Facility Name")
    >>> facility.Title()
    'Updated Facility Name'

Reset the title:

    >>> facility.setTitle("Test Facility")


StorageAssistant CAN create positions
.....................................

StorageAssistant can create `StoragePosition` objects inside a facility:

    >>> position = api.create(facility, "StoragePosition", title="Room A")
    >>> position
    <StoragePosition at /plone/senaite_storage/SF-00001/SP-00001>

    >>> position.Title()
    'Room A'

    >>> position.aq_parent == facility
    True

Create another position for move tests:

    >>> position_b = api.create(facility, "StoragePosition", title="Room B")
    >>> position_b
    <StoragePosition at /plone/senaite_storage/SF-00001/SP-00002>


StorageAssistant CAN edit positions
....................................

StorageAssistant can modify position properties:

    >>> position.setTitle("Cold Room A")
    >>> position.Title()
    'Cold Room A'

Reset the title:

    >>> position.setTitle("Room A")


StorageAssistant CAN create containers
......................................

StorageAssistant can create `StorageContainer` objects inside a position:

    >>> container = api.create(position, "StorageContainer", title="Freezer A")
    >>> container
    <StorageContainer at /plone/senaite_storage/SF-00001/SP-00001/SC-00001>

    >>> container.Title()
    'Freezer A'

    >>> container.aq_parent == position
    True

StorageAssistant can also create containers inside other containers (nested):

    >>> nested_container = api.create(container, "StorageContainer", title="Shelf 1")
    >>> nested_container
    <StorageContainer at /plone/senaite_storage/SF-00001/SP-00001/SC-00001/SC-00002>

    >>> nested_container.Title()
    'Shelf 1'

    >>> nested_container.aq_parent == container
    True


StorageAssistant CAN edit containers
....................................

StorageAssistant can modify container properties:

    >>> container.setTitle("Freezer A-1")
    >>> container.Title()
    'Freezer A-1'

    >>> nested_container.setTitle("Shelf 1-A")
    >>> nested_container.Title()
    'Shelf 1-A'


StorageAssistant CAN create samples containers
..............................................

StorageAssistant can create `StorageSamplesContainer` objects inside a container:

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


StorageAssistant CAN edit samples containers
............................................

StorageAssistant can modify samples container properties:

    >>> samples_container.setTitle("Box A-1")
    >>> samples_container.Title()
    'Box A-1'


StorageAssistant CAN move containers
....................................

The `move_container` transition is available for containers:

    >>> "move_container" in getAllowedTransitions(nested_container)
    True

Move a container from one position to another:

    >>> "/".join(nested_container.getPhysicalPath())
    '/plone/senaite_storage/SF-00001/SP-00001/SC-00001/SC-00002'

    >>> nested_container = api.move_object(nested_container, position_b, check_constraints=False)
    >>> nested_container
    <StorageContainer at /plone/senaite_storage/SF-00001/SP-00002/SC-00002>

    >>> nested_container.aq_parent == position_b
    True

Create another container to test moving inside containers:

    >>> another_container = api.create(position_b, "StorageContainer", title="Cabinet B")
    >>> another_container
    <StorageContainer at /plone/senaite_storage/SF-00001/SP-00002/SC-00003>

Move a container inside another container:

    >>> nested_container = api.move_object(nested_container, another_container, check_constraints=False)
    >>> nested_container
    <StorageContainer at /plone/senaite_storage/SF-00001/SP-00002/SC-00003/SC-00002>

    >>> nested_container.aq_parent == another_container
    True


StorageAssistant CAN move samples containers
............................................

The `move_container` transition is available for samples containers:

    >>> "move_container" in getAllowedTransitions(samples_container)
    True

Check the current location of the samples container:

    >>> "/".join(samples_container.getPhysicalPath())
    '/plone/senaite_storage/SF-00001/SP-00001/SC-00001/SS-00001'

Move the samples container to a different container:

    >>> samples_container = api.move_object(samples_container, another_container, check_constraints=False)
    >>> samples_container
    <StorageSamplesContainer at /plone/senaite_storage/SF-00001/SP-00002/SC-00003/SS-00001>

    >>> samples_container.aq_parent == another_container
    True


StorageAssistant CAN store samples
..................................

First, create and receive a sample as LabClerk:

    >>> setRoles(portal, TEST_USER_ID, ["LabClerk"])

    >>> sample = new_sample([service], client, contact, sampletype)
    >>> api.get_workflow_status_of(sample)
    'sample_due'

    >>> transitioned = do_action_for(sample, "receive")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

Now switch to StorageAssistant role:

    >>> setRoles(portal, TEST_USER_ID, ["StorageAssistant"])

The `store` transition is available for received samples:

    >>> "store" in getAllowedTransitions(sample)
    True

StorageAssistant can store the sample:

    >>> samples_container.add_object_at(sample, 0, 0)
    True

    >>> api.get_workflow_status_of(sample)
    'stored'

    >>> samples_container.get_samples_utilization()
    1


StorageAssistant CAN recover samples
....................................

The `recover` transition is available for stored samples:

    >>> "recover" in getAllowedTransitions(sample)
    True

StorageAssistant can recover samples:

    >>> transitioned = do_action_for(sample, "recover")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

    >>> samples_container.get_samples_utilization()
    0


StorageAssistant CAN store and recover samples created by other users
.....................................................................

Create a sample as LabClerk and store it:

    >>> setRoles(portal, TEST_USER_ID, ["LabClerk"])

    >>> sample2 = new_sample([service], client, contact, sampletype)
    >>> transitioned = do_action_for(sample2, "receive")
    >>> samples_container.add_object_at(sample2, 1, 0)
    True

    >>> api.get_workflow_status_of(sample2)
    'stored'

Switch to StorageAssistant and recover the sample:

    >>> setRoles(portal, TEST_USER_ID, ["StorageAssistant"])

    >>> "recover" in getAllowedTransitions(sample2)
    True

    >>> transitioned = do_action_for(sample2, "recover")
    >>> api.get_workflow_status_of(sample2)
    'sample_received'

Store it again as StorageAssistant:

    >>> samples_container.add_object_at(sample2, 2, 0)
    True

    >>> api.get_workflow_status_of(sample2)
    'stored'

    >>> samples_container.get_samples_utilization()
    1


StorageAssistant CANNOT deactivate containers
.............................................

Create a fresh container to test deactivate/activate permissions:

    >>> test_container = api.create(position_b, "StorageContainer", title="Test Container")
    >>> test_container
    <StorageContainer at /plone/senaite_storage/SF-00001/SP-00002/SC-00004>

StorageAssistant does not have permission to deactivate containers:

    >>> "deactivate" in getAllowedTransitions(test_container)
    False

    >>> transitioned = do_action_for(test_container, "deactivate")
    >>> transitioned[0]
    False

The container remains active:

    >>> api.get_workflow_status_of(test_container)
    'active'


StorageAssistant CANNOT activate containers
...........................................

First, let's deactivate the container as LabManager:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])
    >>> transitioned = do_action_for(test_container, "deactivate")
    >>> api.get_workflow_status_of(test_container)
    'inactive'

Switch back to StorageAssistant:

    >>> setRoles(portal, TEST_USER_ID, ["StorageAssistant"])

StorageAssistant cannot activate the container:

    >>> "activate" in getAllowedTransitions(test_container)
    False

    >>> transitioned = do_action_for(test_container, "activate")
    >>> transitioned[0]
    False

The container remains inactive:

    >>> api.get_workflow_status_of(test_container)
    'inactive'


StorageAssistant CANNOT deactivate samples containers
.....................................................

Create a fresh samples container to test deactivate/activate permissions:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])
    >>> test_sc_container = api.create(position_b, "StorageContainer", title="Test SC Container")
    >>> test_samples_container = api.create(test_sc_container, "StorageSamplesContainer", title="Test Box", Rows=2, Columns=2)

    >>> setRoles(portal, TEST_USER_ID, ["StorageAssistant"])

StorageAssistant does not have permission to deactivate samples containers:

    >>> "deactivate" in getAllowedTransitions(test_samples_container)
    False

    >>> transitioned = do_action_for(test_samples_container, "deactivate")
    >>> transitioned[0]
    False

The samples container remains active:

    >>> api.get_workflow_status_of(test_samples_container)
    'active'


StorageAssistant CANNOT activate samples containers
...................................................

First, let's deactivate the samples container as LabManager:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])
    >>> transitioned = do_action_for(test_samples_container, "deactivate")
    >>> api.get_workflow_status_of(test_samples_container)
    'inactive'

Switch back to StorageAssistant:

    >>> setRoles(portal, TEST_USER_ID, ["StorageAssistant"])

StorageAssistant cannot activate the samples container:

    >>> "activate" in getAllowedTransitions(test_samples_container)
    False

    >>> transitioned = do_action_for(test_samples_container, "activate")
    >>> transitioned[0]
    False

The samples container remains inactive:

    >>> api.get_workflow_status_of(test_samples_container)
    'inactive'


StorageAssistant CANNOT deactivate facilities
.............................................

StorageAssistant does not have permission to deactivate facilities:

    >>> "deactivate" in getAllowedTransitions(facility)
    False

    >>> transitioned = do_action_for(facility, "deactivate")
    >>> transitioned[0]
    False

The facility remains active:

    >>> api.get_workflow_status_of(facility)
    'active'


StorageAssistant CANNOT activate facilities
...........................................

First, let's deactivate the facility as LabManager:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])
    >>> transitioned = do_action_for(facility, "deactivate")
    >>> api.get_workflow_status_of(facility)
    'inactive'

Switch back to StorageAssistant:

    >>> setRoles(portal, TEST_USER_ID, ["StorageAssistant"])

StorageAssistant cannot activate the facility:

    >>> "activate" in getAllowedTransitions(facility)
    False

    >>> transitioned = do_action_for(facility, "activate")
    >>> transitioned[0]
    False

The facility remains inactive:

    >>> api.get_workflow_status_of(facility)
    'inactive'


StorageAssistant CANNOT deactivate positions
............................................

First, reactivate the facility as LabManager so we can test positions:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])
    >>> transitioned = do_action_for(facility, "activate")
    >>> api.get_workflow_status_of(facility)
    'active'

    >>> setRoles(portal, TEST_USER_ID, ["StorageAssistant"])

StorageAssistant does not have permission to deactivate positions:

    >>> "deactivate" in getAllowedTransitions(position)
    False

    >>> transitioned = do_action_for(position, "deactivate")
    >>> transitioned[0]
    False

The position remains active:

    >>> api.get_workflow_status_of(position)
    'active'


StorageAssistant CANNOT activate positions
..........................................

First, let's deactivate the position as LabManager:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])
    >>> transitioned = do_action_for(position, "deactivate")
    >>> api.get_workflow_status_of(position)
    'inactive'

Switch back to StorageAssistant:

    >>> setRoles(portal, TEST_USER_ID, ["StorageAssistant"])

StorageAssistant cannot activate the position:

    >>> "activate" in getAllowedTransitions(position)
    False

    >>> transitioned = do_action_for(position, "activate")
    >>> transitioned[0]
    False

The position remains inactive:

    >>> api.get_workflow_status_of(position)
    'inactive'
