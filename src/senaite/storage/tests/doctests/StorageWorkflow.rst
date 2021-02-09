Storage Workflow
----------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t StorageWorkflow

Test Setup
..........

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def new_sample(services, client, contact, sampletype):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': date_now,
    ...         'SampleType': sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, service_uids)
    ...     return sample

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> storage = portal.senaite_storage

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(setup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Storage setup
.............

Create a storage facility:

    >>> sf = api.create(storage, "StorageFacility", title="SENAITE Storage Facility")
    >>> sf
    <StorageFacility at /plone/senaite_storage/SF-00001>

Create a storage position:

    >>> sp = api.create(sf, "StoragePosition", title="Room A")
    >>> sp
    <StoragePosition at /plone/senaite_storage/SF-00001/SP-00001>

Create a storage container:

    >>> sc = api.create(sp, "StorageContainer", title="Freezer A")
    >>> sc
    <StorageContainer at /plone/senaite_storage/SF-00001/SP-00001/SC-00001>

Create a samples container:

    >>> ssc = api.create(sc, "StorageSamplesContainer", title="3x3 container", Rows=3, Columns=3)
    >>> ssc
    <StorageSamplesContainer at /plone/senaite_storage/SF-00001/SP-00001/SC-00001/SS-00001>

    >>> ssc.getRows()
    3

    >>> ssc.getColumns()
    3

    >>> ssc.get_samples_capacity()
    9


Allowed transitions
...................

Check allowed transitions for the container:

   >>> getAllowedTransitions(sf)
   ['deactivate']

   >>> getAllowedTransitions(sp)
   ['deactivate']

   >>> getAllowedTransitions(sc)
   ['deactivate', 'move_container']

Check allowed transitions for the samples container:

   >>> getAllowedTransitions(ssc)
   ['deactivate', 'move_container', 'add_samples']


Active/Inactive states
......................

Initially, all storage content is in `active` state:

    >>> api.get_workflow_status_of(sf)
    'active'

    >>> api.get_workflow_status_of(sp)
    'active'

    >>> api.get_workflow_status_of(sc)
    'active'

    >>> api.get_workflow_status_of(ssc)
    'active'

Deactivating a storage content will deactivate all contained contents:

    >>> transitioned = do_action_for(sf, "deactivate")
    >>> api.get_workflow_status_of(sf)
    'inactive'

    >>> api.get_workflow_status_of(sp)
    'inactive'

    >>> api.get_workflow_status_of(sc)
    'inactive'

    >>> api.get_workflow_status_of(ssc)
    'inactive'

Activating the storage content again will also activate all contained contents:

    >>> transitioned = do_action_for(sf, "activate")
    >>> api.get_workflow_status_of(sf)
    'active'

    >>> api.get_workflow_status_of(sp)
    'active'

    >>> api.get_workflow_status_of(sc)
    'active'

    >>> api.get_workflow_status_of(ssc)
    'active'


Adding samples to the storage
.............................

Create a new sample:

    >>> sample = new_sample([Cu, Fe, Au], client, contact, sampletype)
    >>> api.get_workflow_status_of(sample)
    'sample_due'

Only received samples can be stored:

    >>> "store" in getAllowedTransitions(sample)
    False

Receive the sample:

    >>> transitioned = do_action_for(sample, "receive")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

Now the sample can be stored:

    >>> ssc.add_object_at(sample, 0, 0)
    True

    >>> api.get_workflow_status_of(sample)
    'stored'

    >>> ssc.get_samples_utilization()
    1


Recovering stored samples
.........................

As soon as a samples container has stored samples, the `recover_samples`
transition is available:

   >>> getAllowedTransitions(ssc)
   ['deactivate', 'move_container', 'add_samples', 'recover_samples']

Recovering a sample restores the previous workflow state of the sample:

    >>> transitioned = do_action_for(sample, "recover")

    >>> api.get_workflow_status_of(sample)
    'sample_received'

    >>> ssc.get_samples_utilization()
    0

Deactivating a storage keeps all stored samples:

    >>> ssc.add_object_at(sample, 0, 0)
    True

    >>> api.get_workflow_status_of(sample)
    'stored'

    >>> transitioned = do_action_for(ssc, "deactivate")

    >>> api.get_workflow_status_of(ssc)
    'inactive'

    >>> ssc.get_samples_utilization()
    1

    >>> api.get_workflow_status_of(sample)
    'stored'

    >>> transitioned = do_action_for(ssc, "activate")

    >>> api.get_workflow_status_of(ssc)
    'active'


Dispatching stored samples
..........................

Stored samples can be dispatched:

    >>> transitioned = do_action_for(sample, "dispatch")

    >>> api.get_workflow_status_of(sample)
    'dispatched'

Dispatched samples will be automatically recovered from the storage first:

    >>> ssc.has_samples()
    False

    >>> ssc.get_samples_utilization()
    0

Dispatched samples can not be stored anymore:

   >>> "store" in getAllowedTransitions(sample)
   False
