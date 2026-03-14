Unmanaged Containers
--------------------

Running this test from the buildout directory:

    bin/test test_doctests -t UnmanagedContainers

Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Functional Helpers:

    >>> def new_sample(services, client, contact, sampletype):
    ...     values = {
    ...         "Client": client.UID(),
    ...         "Contact": contact.UID(),
    ...         "DateSampled": DateTime().strftime("%Y-%m-%d"),
    ...         "SampleType": sampletype.UID(),
    ...     }
    ...     service_uids = map(api.get_uid, services)
    ...     return create_analysisrequest(client, request, values, service_uids)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()
    >>> storage = portal.senaite_storage

Basic setup
...........

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(portal.setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(portal.setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(portal.setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> service = api.create(setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)

    >>> facility = api.create(storage, "StorageFacility", title="Storage Facility")
    >>> position = api.create(facility, "StoragePosition", title="Room A")
    >>> container = api.create(position, "StorageContainer", title="Freezer A")

Unmanaged containers store samples without fixed positions
..........................................................

    >>> unmanaged = api.create(container, "StorageSamplesContainer", title="Bag A", Managed=False)
    >>> unmanaged.is_managed()
    False

    >>> unmanaged.requires_position_tracking()
    False

    >>> unmanaged.get_available_positions()
    []

    >>> sample = new_sample([service], client, contact, sampletype)
    >>> api.get_workflow_status_of(sample)
    'sample_due'

    >>> do_action_for(sample, "receive")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

    >>> unmanaged.add_object(sample)
    True

    >>> api.get_workflow_status_of(sample)
    'stored'

    >>> unmanaged.get_samples_utilization()
    1

    >>> unmanaged.get_samples_capacity()
    1

    >>> unmanaged.is_full()
    False

Configurable physical capacity is enforced for unmanaged containers
...................................................................

    >>> limited = api.create(container, "StorageSamplesContainer", title="Bag B", Managed=False, PhysicalCapacity=2)
    >>> limited.get_capacity_limit()
    2

    >>> sample_1 = new_sample([service], client, contact, sampletype)
    >>> sample_2 = new_sample([service], client, contact, sampletype)
    >>> sample_3 = new_sample([service], client, contact, sampletype)

    >>> do_action_for(sample_1, "receive")
    >>> do_action_for(sample_2, "receive")
    >>> do_action_for(sample_3, "receive")

    >>> limited.add_object(sample_1)
    True

    >>> limited.add_object(sample_2)
    True

    >>> limited.get_samples_utilization()
    2

    >>> limited.is_full()
    True

    >>> limited.add_object(sample_3)
    False

    >>> api.get_workflow_status_of(sample_3)
    'sample_received'
