Primary Sample
--------------

When using partitions, `senaite.storage` automatically transitions the primary
samples for them to follow the status of their partitions. This applies for
both `store` and `recover` transitions. Although this is the behavior set by
default, user can change it from Storage's control panel, under Site setup.

Test Setup
..........

Running this test from the buildout directory:

    bin/test -t PrimarySample

Needed Imports:

    >>> from bika.lims import api
    >>> #from bika.lims.api.security import get_valid_roles_for
    >>> #from bika.lims.api.security import revoke_permission_for
    >>> #from bika.lims.permissions import TransitionReceiveSample
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Functional Helpers:

    >>> def new_sample_container(**kwargs):
    ...     return api.create(sc, "StorageSamplesContainer", **kwargs)

    >>> def new_sample(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': sampletype.UID()}
    ...     uids = map(api.get_uid, services)
    ...     return create_analysisrequest(client, request, values, uids)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()
    >>> storage = portal.senaite_storage

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

Setup baseline storage objects for the test:

    >>> sf = api.create(storage, "StorageFacility", title="Storage facility")
    >>> sp = api.create(sf, "StoragePosition", title="Room A")
    >>> sc = api.create(sp, "StorageContainer", title="Freezer A")

Create some baseline objects for the test:

    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(setup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())

Auto-transition primary sample
..............................

Create a sample container:

    >>> ssc = new_sample_container(title="3x3", Rows=3, Columns=3)

Create a Sample and two partitions:

    >>> sample = new_sample([Fe, Au])
    >>> transitioned = do_action_for(sample, "receive")
    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> part1 = create_partition(sample, request, [analyses[0]])
    >>> part2 = create_partition(sample, request, [analyses[1]])

Store the partition 1:

    >>> ssc.add_object_at(part1, 0, 0)
    True
    >>> api.get_review_status(part1)
    'stored'

Both the primary and partition 2 remain in `sample_received` status:

    >>> api.get_review_status(sample)
    'sample_received'
    >>> api.get_review_status(part2)
    'sample_received'

Store the partition 2:

    >>> ssc.add_object_at(part2, 0, 1)
    True
    >>> api.get_review_status(part2)
    'stored'

The primary is automatically transitioned to `stored` status too:

    >>> api.get_review_status(sample)
    'stored'

Restore the partition 1:

    >>> transitioned = do_action_for(part1, "recover")
    >>> api.get_review_status(part1)
    'sample_received'
    >>> api.get_review_status(part2)
    'stored'
    >>> api.get_review_status(sample)
    'stored'

Restore the partition 2:

    >>> transitioned = do_action_for(part2, "recover")
    >>> api.get_review_status(part2)
    'sample_received'

The primary sample is transitioned to `sample_received` as well:

    >>> api.get_review_status(sample)
    'sample_received'
