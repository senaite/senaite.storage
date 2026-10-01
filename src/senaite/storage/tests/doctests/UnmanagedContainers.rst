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

    >>> success = do_action_for(sample, "receive")
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

    >>> success = do_action_for(sample_1, "receive")
    >>> success = do_action_for(sample_2, "receive")
    >>> success = do_action_for(sample_3, "receive")

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

The mode cannot change while the container holds samples
........................................................

Changing the mode of a container that holds samples would drop them from the
layout (unmanaged to managed) or leave them with stale positions, so it is
rejected. The form invariant is what protects the edit form:

    >>> from zope.interface import Invalid
    >>> from senaite.storage.content.storage_samples_container import IStorageSamplesContainerSchema

    >>> class FormData(object):
    ...     rows = 1
    ...     columns = 1
    ...     physical_capacity = None
    ...     def __init__(self, context, managed):
    ...         self.__context__ = context
    ...         self.managed = managed

    >>> def check_form(container, managed):
    ...     try:
    ...         IStorageSamplesContainerSchema.validateInvariants(FormData(container, managed))
    ...     except Invalid as e:
    ...         return str(e)
    ...     return "valid"

``unmanaged`` still holds the first sample, so it cannot become managed:

    >>> unmanaged.has_samples()
    True

    >>> check_form(unmanaged, True)
    'Cannot change the container mode while it holds samples. Retrieve them first.'

    >>> unmanaged.setManaged(True)
    Traceback (most recent call last):
    ...
    ValueError: Cannot change the container mode while it holds samples

    >>> unmanaged.is_managed()
    False

    >>> len(unmanaged.get_samples_uids())
    1

Keeping the same mode is always fine:

    >>> check_form(unmanaged, False)
    'valid'

The same applies to a managed container with a stored sample:

    >>> box = api.create(container, "StorageSamplesContainer", title="Box", Rows=2, Columns=2)
    >>> sample_4 = new_sample([service], client, contact, sampletype)
    >>> success = do_action_for(sample_4, "receive")
    >>> box.add_object_at(sample_4, 0, 0)
    True

    >>> check_form(box, False)
    'Cannot change the container mode while it holds samples. Retrieve them first.'

    >>> box.setManaged(False)
    Traceback (most recent call last):
    ...
    ValueError: Cannot change the container mode while it holds samples

    >>> box.is_managed()
    True

Once the samples are retrieved, the mode can change:

    >>> success = do_action_for(sample, "recover")
    >>> unmanaged.has_samples()
    False

    >>> check_form(unmanaged, True)
    'valid'

    >>> unmanaged.setManaged(True)
    >>> unmanaged.is_managed()
    True

    >>> success = do_action_for(sample_4, "recover")
    >>> box.setManaged(False)
    >>> box.is_managed()
    False

The edit form does not go through ``setManaged``, so the modified event must
rebuild the layout when the mode changes. Otherwise an empty unmanaged
container switched to managed would have no positions to store samples in:

    >>> from zope.event import notify
    >>> from zope.lifecycleevent import Attributes
    >>> from zope.lifecycleevent import ObjectModifiedEvent

    >>> flip = api.create(container, "StorageSamplesContainer", title="Flip", Managed=False)
    >>> len(flip.getPositionsLayout())
    0

    >>> flip.managed = True
    >>> notify(ObjectModifiedEvent(flip, Attributes(IStorageSamplesContainerSchema, "managed")))
    >>> len(flip.getPositionsLayout())
    1

    >>> flip.get_available_positions()
    [(0, 0)]
