Retrieve Reasons
----------------

When retrieving samples from storage, laboratories can require users to
select a reason. Reasons are configured in the Storage control panel and
stored on the sample for audit purposes.

Running this test from the buildout directory:

    bin/test -t RetrieveReasons

Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.storage import api as storage_api

Functional Helpers:

    >>> def new_sample(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': sampletype.UID()}
    ...     uids = map(api.get_uid, services)
    ...     return create_analysisrequest(client, request, values, uids)

    >>> def set_retrieve_reasons(reasons):
    ...     key = "senaite.storage.retrieve_reasons"
    ...     ploneapi.portal.set_registry_record(key, reasons)

    >>> def set_require_retrieve_reason(required):
    ...     key = "senaite.storage.require_retrieve_reason"
    ...     ploneapi.portal.set_registry_record(key, required)

    >>> def store_sample(sample, container, row, col):
    ...     container.add_object_at(sample, row, col)
    ...     return sample

    >>> def receive_sample(sample):
    ...     do_action_for(sample, "receive")
    ...     return sample

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bika_setup = portal.bika_setup
    >>> storage = portal.senaite_storage

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

Create baseline objects:

    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> labcontact = api.create(bika_setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())

Setup storage structure:

    >>> sf = api.create(storage, "StorageFacility", title="Storage facility")
    >>> sp = api.create(sf, "StoragePosition", title="Room A")
    >>> sc = api.create(sp, "StorageContainer", title="Freezer A")
    >>> ssc = api.create(sc, "StorageSamplesContainer", title="3x3 container", Rows=3, Columns=3)


No reasons configured
.....................

When no retrieve reasons are configured, ``get_retrieve_reasons`` returns an
empty list and ``is_retrieve_reason_required`` returns False:

    >>> storage_api.get_retrieve_reasons()
    []

    >>> storage_api.is_retrieve_reason_required()
    False

The retrieve reason field on a sample defaults to empty:

    >>> sample1 = receive_sample(new_sample([Cu, Fe]))
    >>> sample1.getRetrieveReason()
    ''

Store and retrieve the sample without a reason:

    >>> store_sample(sample1, ssc, 0, 0)
    <AnalysisRequest at ...>

    >>> api.get_workflow_status_of(sample1)
    'stored'

    >>> do_action_for(sample1, "recover")
    (...)

    >>> api.get_workflow_status_of(sample1)
    'sample_received'

The reason remains empty:

    >>> sample1.getRetrieveReason()
    ''


Configuring retrieve reasons
.............................

Configure retrieve reasons in the registry:

    >>> reasons = [
    ...     u"Further analysis required",
    ...     u"Sample re-testing",
    ...     u"Client request",
    ... ]
    >>> set_retrieve_reasons(reasons)

    >>> storage_api.get_retrieve_reasons()
    [u'Further analysis required', u'Sample re-testing', u'Client request']

By default, selecting a reason is not required:

    >>> storage_api.is_retrieve_reason_required()
    False

Enable the requirement:

    >>> set_require_retrieve_reason(True)

    >>> storage_api.is_retrieve_reason_required()
    True


Storing retrieve reason on sample
..................................

Store the sample again:

    >>> store_sample(sample1, ssc, 0, 0)
    <AnalysisRequest at ...>

    >>> api.get_workflow_status_of(sample1)
    'stored'

Set a retrieve reason and recover the sample:

    >>> sample1.setRetrieveReason("Further analysis required")
    >>> do_action_for(sample1, "recover")
    (...)

    >>> api.get_workflow_status_of(sample1)
    'sample_received'

The reason is persisted on the sample:

    >>> sample1.getRetrieveReason()
    'Further analysis required'


Reason cleared on re-store
...........................

When a sample is stored again, the reason from the previous cycle is cleared:

    >>> store_sample(sample1, ssc, 0, 0)
    <AnalysisRequest at ...>

    >>> sample1.getRetrieveReason()
    ''

A new reason can be set for this cycle:

    >>> sample1.setRetrieveReason("Client request")
    >>> do_action_for(sample1, "recover")
    (...)

    >>> sample1.getRetrieveReason()
    'Client request'


Multiple samples
................

Create a second sample and store both:

    >>> sample2 = receive_sample(new_sample([Cu]))
    >>> store_sample(sample1, ssc, 0, 0)
    <AnalysisRequest at ...>
    >>> store_sample(sample2, ssc, 0, 1)
    <AnalysisRequest at ...>

Each sample can have its own retrieve reason:

    >>> sample1.setRetrieveReason("Sample re-testing")
    >>> sample2.setRetrieveReason("Client request")

    >>> do_action_for(sample1, "recover")
    (...)
    >>> do_action_for(sample2, "recover")
    (...)

    >>> sample1.getRetrieveReason()
    'Sample re-testing'

    >>> sample2.getRetrieveReason()
    'Client request'


Disabling retrieve reasons
..........................

Remove all reasons and disable the requirement:

    >>> set_retrieve_reasons([])
    >>> set_require_retrieve_reason(False)

    >>> storage_api.get_retrieve_reasons()
    []

    >>> storage_api.is_retrieve_reason_required()
    False
