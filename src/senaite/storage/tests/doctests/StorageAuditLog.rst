Storage Audit Log
-----------------

The link between a sample and the position it occupies lives in exactly one
place: the layout of the container that holds it. Nothing is written to the
sample itself. For that link to survive a container being emptied, cleared
or deleted, every placement and every removal has to leave an entry in the
audit log.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t StorageAuditLog

Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.core.api.snapshot import get_snapshots

Functional Helpers:

    >>> def new_sample(services, client, contact, sampletype):
    ...     values = {
    ...         "Client": client.UID(),
    ...         "Contact": contact.UID(),
    ...         "DateSampled": date_now,
    ...         "SampleType": sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     return create_analysisrequest(client, request, values, service_uids)

    >>> def get_audited_layouts(container):
    ...     """Sample uids the container held, per audit log entry"""
    ...     layouts = []
    ...     for snapshot in get_snapshots(container):
    ...         layout = snapshot.get("positions_layout") or []
    ...         uids = [pos.get("uid") for pos in layout if pos.get("uid")]
    ...         layouts.append(uids)
    ...     return layouts

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> storage = portal.senaite_storage

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(portal.setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(portal.setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(portal.setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID())

Storage setup
.............

    >>> sf = api.create(storage, "StorageFacility", title="Storage Facility")
    >>> sp = api.create(sf, "StoragePosition", title="Room A")
    >>> sc = api.create(sp, "StorageContainer", title="Freezer A")
    >>> ssc = api.create(sc, "StorageSamplesContainer", title="3x3 container", Rows=3, Columns=3)


A new container is audited, and holds nothing
.............................................

    >>> layouts = get_audited_layouts(ssc)
    >>> len(layouts) > 0
    True

    >>> layouts[-1]
    []


Storing a sample is recorded
............................

Only received samples can be stored:

    >>> sample = new_sample([Cu], client, contact, sampletype)
    >>> transitioned = do_action_for(sample, "receive")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

    >>> ssc.add_object_at(sample, 0, 0)
    True

    >>> api.get_workflow_status_of(sample)
    'stored'

The container holds it:

    >>> api.get_uid(sample) in ssc.get_samples_uids()
    True

And the placement left a new entry in the audit log:

    >>> layouts = get_audited_layouts(ssc)
    >>> layouts[-1] == [api.get_uid(sample)]
    True


Retrieving the sample is recorded too
.....................................

Retrieving the sample both empties the position and transitions the sample
out of `stored`:

    >>> transitioned = do_action_for(sample, "recover")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

    >>> ssc.get_samples_uids()
    []

The audit log now holds the removal as well:

    >>> layouts = get_audited_layouts(ssc)
    >>> layouts[-1]
    []

The container no longer refers to the sample, but its history still records
that it once held it:

    >>> uids_ever_held = [uid for layout in layouts for uid in layout]
    >>> api.get_uid(sample) in uids_ever_held
    True

This is what makes an emptied or deleted container recoverable. Without it
the only snapshot ever taken is the one above, from when the container was
created and still empty, and the position a sample occupied is lost the
moment it leaves the layout.


A sample that cannot be stored does not occupy a position
.........................................................

The position is written to the layout before the sample is transitioned.
If the transition is not allowed, the write is undone, so a sample never
occupies a position without being stored:

    >>> from bika.lims.workflow import getAllowedTransitions
    >>> other = new_sample([Cu], client, contact, sampletype)
    >>> "store" in getAllowedTransitions(other)
    False

    >>> snapshots_count = len(get_snapshots(ssc))
    >>> ssc.add_object_at(other, 2, 2)
    False

    >>> api.get_uid(other) in ssc.get_samples_uids()
    False

    >>> ssc.is_empty_position(2, 2)
    True

And nothing was recorded, because nothing happened:

    >>> len(get_snapshots(ssc)) == snapshots_count
    True


The catalog is kept in sync as well
...................................

The same notification keeps the storage catalog current, so a retrieved
sample stops being reported as contained:

    >>> from senaite.storage.api import get_storage_sample
    >>> get_storage_sample(sample) is None
    True

    >>> ssc.add_object_at(sample, 1, 1)
    True

    >>> get_storage_sample(sample) == ssc
    True
