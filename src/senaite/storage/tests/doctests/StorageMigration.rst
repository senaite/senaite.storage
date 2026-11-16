Storage Migration
-----------------

The storage contents were migrated from Archetypes to Dexterity in 2.7.0. A
storage container keeps, for each of its positions, the UID of what it holds,
so the migration must keep the dimensions and layouts of the containers and
the UIDs of their contents. Sites migrated before this was fixed get their
dimensions and layouts restored by an upgrade step.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t StorageMigration

Test Setup
..........

Needed Imports:

    >>> import json
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.core.api import snapshot as snapshot_api
    >>> from senaite.core.migration.migrator import ATTRIBUTE_STORAGE
    >>> from senaite.storage.api import get_storage_sample
    >>> from senaite.storage.content.storagecontainer import \
    ...     StorageContainer as ATStorageContainer
    >>> from senaite.storage.content.storagesamplescontainer import \
    ...     StorageSamplesContainer as ATSamplesContainer
    >>> from senaite.storage.upgrade import v02_07_000 as steps
    >>> from zope.annotation.interfaces import IAnnotations

Functional Helpers:

    >>> def new_sample():
    ...     values = {
    ...         "Client": client.UID(),
    ...         "Contact": contact.UID(),
    ...         "DateSampled": DateTime().strftime("%Y-%m-%d"),
    ...         "SampleType": sampletype.UID()}
    ...     sample = create_analysisrequest(
    ...         client, request, values, [api.get_uid(Cu)])
    ...     do_action_for(sample, "receive")
    ...     return sample

    >>> def get_layout(container):
    ...     layout = container.getPositionsLayout()
    ...     return [(item["row"], item["column"],
    ...              api.get_object_by_uid(item["uid"]).getId())
    ...             for item in layout if item.get("uid")]

    >>> def get_capacity(container, child):
    ...     uid = api.get_uid(child)
    ...     layout = container.getPositionsLayout()
    ...     return [item["samples_capacity"] for item in layout
    ...             if item.get("uid") == uid]

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()
    >>> portal_setup = portal.portal_setup
    >>> storage = portal.senaite_storage
    >>> setRoles(portal, TEST_USER_ID, ["LabManager", "Manager"])

Baseline objects:

    >>> client = api.create(portal.clients, "Client", Name="Happy Hills",
    ...                     ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita",
    ...                      Lastname="Mohale")
    >>> sampletype = api.create(portal.setup.sampletypes, "SampleType",
    ...                         title="Water", Prefix="W")
    >>> Cu = api.create(setup.bika_analysisservices, "AnalysisService",
    ...                 title="Copper", Keyword="Cu")
    >>> facility = api.create(storage, "StorageFacility", title="Facility")
    >>> room = api.create(facility, "StoragePosition", title="Room")


Migration of the containers
...........................

A rack of 2 x 2 positions holds a box of 2 rows and 3 columns, at the position
B2:

    >>> room._setObject("at-rack", ATStorageContainer("at-rack"))
    'at-rack'
    >>> at_rack = room._getOb("at-rack")
    >>> at_rack.setRows(2)
    >>> at_rack.setColumns(2)
    >>> at_rack._setObject("at-box", ATSamplesContainer("at-box"))
    'at-box'
    >>> at_box = at_rack._getOb("at-box")
    >>> at_box.setRows(2)
    >>> at_box.setColumns(3)
    >>> at_rack.add_object_at(at_box, 1, 1)
    True
    >>> box_uid = api.get_uid(at_box)

The rack keeps its dimensions and the position of the box when it is migrated.
The box is moved into the migrated rack, so it keeps its UID:

    >>> steps.migrate_storage_container_to_dx(at_rack, room)
    >>> rack = room._getOb("at-rack")
    >>> api.is_dexterity_content(rack)
    True
    >>> rack.getRows(), rack.getColumns()
    (2, 2)
    >>> api.get_uid(rack._getOb("at-box")) == box_uid
    True
    >>> get_layout(rack)
    [(1, 1, 'at-box')]

The box keeps its rows and columns:

    >>> steps.migrate_storage_samples_container_to_dx(
    ...     rack._getOb("at-box"), rack)
    >>> box = rack._getOb("at-box")
    >>> api.is_dexterity_content(box), api.get_uid(box) == box_uid
    (True, True)
    >>> box.getRows(), box.getColumns()
    (2, 3)
    >>> get_layout(rack)
    [(1, 1, 'at-box')]
    >>> get_capacity(rack, box)
    [6]


Restore of the containers migrated before the fix
..................................................

The former migration swapped the rows and columns of the samples containers,
did not migrate the dimensions and layout of the storage containers, and gave
the contents of the migrated objects new UIDs. It kept the attributes of the
AT objects though, which the restore relies on.

A rack that was 2 x 2 in AT was left with 1 x 1 positions:

    >>> old_rack = api.create(room, "StorageContainer", title="Old rack")
    >>> old_rack.getRows(), old_rack.getColumns()
    (1, 1)

The box it holds was 2 rows and 3 columns in AT, with three samples at A1, A3
and B3, and became 3 rows and 2 columns. It got a new UID, and its audit log
still has the former one:

    >>> old_box = api.create(old_rack, "StorageSamplesContainer",
    ...                      title="Old box", rows=3, columns=2)
    >>> former_box_uid = "0" * 32
    >>> snapshot_api.get_storage(old_box).append(
    ...     json.dumps({"uid": former_box_uid}))

    >>> sample_a = new_sample()
    >>> sample_b = new_sample()
    >>> sample_c = new_sample()
    >>> sample_d = new_sample()

    >>> def item(row, column, obj, uid=None):
    ...     return {"row": row, "column": column,
    ...             "uid": uid or api.get_uid(obj),
    ...             "samples_capacity": 1, "samples_utilization": 1}

    >>> IAnnotations(old_rack)[ATTRIBUTE_STORAGE] = {
    ...     "Rows": 2, "Columns": 2,
    ...     "PositionsLayout": [item(1, 0, None, uid=former_box_uid)]}
    >>> IAnnotations(old_box)[ATTRIBUTE_STORAGE] = {
    ...     "Rows": 2, "Columns": 3,
    ...     "PositionsLayout": [item(0, 0, sample_a), item(0, 2, sample_b),
    ...                         item(1, 2, sample_c)]}

The layout of the box was copied as it was, but the first sample stored
afterwards, at E2 of the swapped box, rebuilt it with 3 x 2 positions. The
samples at A3 and B3 were dropped, while they are still stored:

    >>> old_box.add_object_at(sample_a, 0, 0)
    True
    >>> old_box.add_object_at(sample_b, 1, 0)
    True
    >>> old_box.add_object_at(sample_c, 1, 1)
    True
    >>> old_box.positions_layout = [
    ...     item for item in old_box.getPositionsLayout()
    ...     if item.get("uid") not in map(api.get_uid, [sample_b, sample_c])]
    >>> old_box.rebuild_layout()
    >>> old_box.reindexObject()
    >>> old_box.add_object_at(sample_d, 2, 1)
    True
    >>> get_storage_sample(sample_b) is None
    True
    >>> api.get_review_status(sample_b)
    'stored'

The rack does not know the box at its former position:

    >>> old_rack.positions_layout = [old_rack.get_default_layout_item()]
    >>> old_rack.rebuild_layout()
    >>> get_layout(old_rack)
    []

The upgrade step restores the dimensions:

    >>> steps.restore_migrated_layouts(portal_setup)
    >>> old_rack.getRows(), old_rack.getColumns()
    (2, 2)
    >>> old_box.getRows(), old_box.getColumns()
    (2, 3)

The samples are back at their AT positions. The one stored at a position the
box does not have takes the first free position:

    >>> ids = dict((api.get_id(s), name) for s, name in [
    ...     (sample_a, "a"), (sample_b, "b"), (sample_c, "c"),
    ...     (sample_d, "d")])
    >>> [(row, column, ids[sid]) for row, column, sid in get_layout(old_box)]
    [(0, 0, 'a'), (0, 1, 'd'), (0, 2, 'b'), (1, 2, 'c')]
    >>> get_storage_sample(sample_b) == old_box
    True

The rack holds the box at its AT position, found by its former UID, with the
capacity of the box:

    >>> get_layout(old_rack) == [(1, 0, api.get_id(old_box))]
    True
    >>> get_capacity(old_rack, old_box)
    [6]

The containers migrated with the fix are left as they are:

    >>> rack.getRows(), rack.getColumns(), get_layout(rack)
    (2, 2, [(1, 1, 'at-box')])
    >>> box.getRows(), box.getColumns()
    (2, 3)

Running the step again changes nothing:

    >>> steps.restore_migrated_layouts(portal_setup)
    >>> [(row, column, ids[sid]) for row, column, sid in get_layout(old_box)]
    [(0, 0, 'a'), (0, 1, 'd'), (0, 2, 'b'), (1, 2, 'c')]
    >>> get_layout(old_rack) == [(1, 0, api.get_id(old_box))]
    True

A container whose dimensions were changed since the migration is left as it
is:

    >>> old_box.rows = 4
    >>> old_box.columns = 4
    >>> old_box.rebuild_layout()
    >>> steps.restore_migrated_layouts(portal_setup)
    >>> old_box.getRows(), old_box.getColumns()
    (4, 4)
