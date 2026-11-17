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

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.core.migration.migrator import ATTRIBUTE_STORAGE
    >>> from senaite.storage.api import get_storage_sample
    >>> from senaite.storage.content.storagecontainer import \
    ...     StorageContainer as ATStorageContainer
    >>> from senaite.storage.content.storagefacility import \
    ...     StorageFacility as ATStorageFacility
    >>> from senaite.storage.content.storagerootfolder import \
    ...     StorageRootFolder as ATStorageRootFolder
    >>> from senaite.storage.content.storagesamplescontainer import \
    ...     StorageSamplesContainer as ATSamplesContainer
    >>> from senaite.storage.tests import old_migration
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

    >>> def layout_item(row, column, obj, uid=None):
    ...     return {"row": row, "column": column,
    ...             "uid": uid or api.get_uid(obj),
    ...             "samples_capacity": 1, "samples_utilization": 1}

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


Sites migrated before the fix
.............................

The former migration copied the contents of the migrated objects, so they got
new UIDs, did not migrate the dimensions and layout of the storage containers,
and swapped the rows and columns of the samples containers. It kept the
attributes of the AT objects though, which the restore relies on.

A site with the AT storage of the former versions has a rack of 2 x 2
positions, with a square box at A1 and a box of 2 rows and 3 columns at B2.
The box has samples at A1, A3 and B3, the square box one at B2:

    >>> portal._delObject("senaite_storage", suppress_events=True)
    >>> portal._setObject("senaite_storage",
    ...                   ATStorageRootFolder("senaite_storage"))
    'senaite_storage'
    >>> at_root = portal._getOb("senaite_storage")
    >>> at_root._setObject("facility", ATStorageFacility("facility"))
    'facility'
    >>> at_facility = at_root._getOb("facility")
    >>> at_facility._setObject("rack", ATStorageContainer("rack"))
    'rack'
    >>> at_rack = at_facility._getOb("rack")
    >>> at_rack.setRows(2)
    >>> at_rack.setColumns(2)
    >>> at_rack._setObject("square", ATSamplesContainer("square"))
    'square'
    >>> at_rack._setObject("box", ATSamplesContainer("box"))
    'box'
    >>> at_square = at_rack._getOb("square")
    >>> at_square.setRows(2)
    >>> at_square.setColumns(2)
    >>> at_box = at_rack._getOb("box")
    >>> at_box.setRows(2)
    >>> at_box.setColumns(3)

The rack took the boxes in at its first free positions when they were added.
They are stored at A1 and B2:

    >>> at_rack.remove_object(at_square)
    True
    >>> at_rack.remove_object(at_box)
    True
    >>> at_rack.add_object_at(at_square, 0, 0)
    True
    >>> at_rack.add_object_at(at_box, 1, 1)
    True

    >>> sample_a = new_sample()
    >>> sample_b = new_sample()
    >>> sample_c = new_sample()
    >>> sample_g = new_sample()
    >>> at_box.add_object_at(sample_a, 0, 0)
    True
    >>> at_box.add_object_at(sample_b, 0, 2)
    True
    >>> at_box.add_object_at(sample_c, 1, 2)
    True
    >>> at_square.add_object_at(sample_g, 1, 1)
    True

    >>> names = dict((api.get_id(obj), name) for obj, name in [
    ...     (sample_a, "a"), (sample_b, "b"), (sample_c, "c"),
    ...     (sample_g, "g")])
    >>> def get_samples(container):
    ...     return [(row, column, names[sid])
    ...             for row, column, sid in get_layout(container)]

The former migration runs:

    >>> former_uids = map(api.get_uid, [at_rack, at_square, at_box])
    >>> old_migration.migrate(portal_setup)
    >>> rack = portal.senaite_storage.facility.rack
    >>> box = rack.box
    >>> square = rack.square
    >>> api.is_dexterity_content(rack), api.is_dexterity_content(box)
    (True, True)

The rack and the boxes got new UIDs:

    >>> [api.get_uid(obj) in former_uids for obj in (rack, square, box)]
    [False, False, False]

The rack lost its dimensions and its layout, and the box got its rows and
columns swapped:

    >>> rack.getRows(), rack.getColumns(), get_layout(rack)
    (1, 1, [])
    >>> box.getRows(), box.getColumns()
    (3, 2)

The migration rebuilt the layout of the box with the swapped dimensions, so
the samples at A3 and B3 were dropped, while they are still stored:

    >>> get_samples(box)
    [(0, 0, 'a')]
    >>> get_storage_sample(sample_b) is None
    True
    >>> api.get_review_status(sample_b)
    'stored'

The square box kept its dimensions and samples:

    >>> square.getRows(), square.getColumns(), get_samples(square)
    (2, 2, [(1, 1, 'g')])

A sample is stored afterwards at E2 of the swapped box:

    >>> sample_d = new_sample()
    >>> names[api.get_id(sample_d)] = "d"
    >>> box.add_object_at(sample_d, 2, 1)
    True

The box was modified, so the rack took it in at its single position:

    >>> get_layout(rack)
    [(0, 0, 'box')]

A sample of the square box lost its position for a reason that has nothing
to do with the migration:

    >>> square.positions_layout = [
    ...     item for item in square.getPositionsLayout()
    ...     if item.get("uid") != api.get_uid(sample_g)]
    >>> square.rebuild_layout()
    >>> square.reindexObject()
    >>> get_storage_sample(sample_g) is None
    True

The upgrade step restores the dimensions:

    >>> steps.restore_migrated_layouts(portal_setup)
    >>> rack.getRows(), rack.getColumns()
    (2, 2)
    >>> box.getRows(), box.getColumns()
    (2, 3)

The samples are back at their AT positions. The one stored at a position the
box does not have takes the first free position:

    >>> get_samples(box)
    [(0, 0, 'a'), (0, 1, 'd'), (0, 2, 'b'), (1, 2, 'c')]
    >>> get_storage_sample(sample_b) == box
    True

The migration did not damage the square box, so the restore leaves it as it
is:

    >>> square.getRows(), square.getColumns(), get_samples(square)
    (2, 2, [])
    >>> get_storage_sample(sample_g) is None
    True

The rack holds the boxes at their AT positions, with their capacities, rather
than where it took them in after the migration. Its AT layout refers to them
by the UIDs they had before the migration, which the original objects the
migration kept still have:

    >>> get_layout(rack)
    [(0, 0, 'square'), (1, 1, 'box')]
    >>> get_capacity(rack, square), get_capacity(rack, box)
    ([4], [6])

Running the step again changes nothing:

    >>> steps.restore_migrated_layouts(portal_setup)
    >>> get_samples(box)
    [(0, 0, 'a'), (0, 1, 'd'), (0, 2, 'b'), (1, 2, 'c')]
    >>> get_layout(rack)
    [(0, 0, 'square'), (1, 1, 'box')]

A container whose dimensions were changed since the migration is left as it
is:

    >>> box.rows = 4
    >>> box.columns = 4
    >>> box.rebuild_layout()
    >>> steps.restore_migrated_layouts(portal_setup)
    >>> box.getRows(), box.getColumns()
    (4, 4)


Migration of the containers
...........................

With the fix, a rack of 2 x 2 positions holding a box of 2 rows and 3
columns at B2:

    >>> storage = portal.senaite_storage
    >>> facility = api.create(storage, "StorageFacility", title="Facility")
    >>> room = api.create(facility, "StoragePosition", title="Room")

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

The rack took the box in at its first free position when it was added. It
is stored at B2:

    >>> at_rack.remove_object(at_box)
    True
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

The restore leaves the containers migrated with the fix as they are, also
when their layout misses a container for another reason:

    >>> spare = api.create(rack, "StorageSamplesContainer", title="Spare",
    ...                    rows=1, columns=1)
    >>> rack.remove_object(spare)
    True
    >>> steps.restore_migrated_layouts(portal_setup)
    >>> rack.getRows(), rack.getColumns(), get_layout(rack)
    (2, 2, [(1, 1, 'at-box')])
    >>> box.getRows(), box.getColumns(), get_capacity(rack, box)
    (2, 3, [6])


The contents of a migrated storage facility are moved as well:

    >>> storage._setObject("at-facility", ATStorageFacility("at-facility"))
    'at-facility'
    >>> at_facility = storage._getOb("at-facility")
    >>> at_facility._setObject("at-freezer", ATStorageContainer("at-freezer"))
    'at-freezer'
    >>> freezer_uid = api.get_uid(at_facility._getOb("at-freezer"))
    >>> steps.migrate_storage_facility_to_dx(at_facility, storage)
    >>> migrated_facility = storage._getOb("at-facility")
    >>> api.is_dexterity_content(migrated_facility)
    True
    >>> api.get_uid(migrated_facility._getOb("at-freezer")) == freezer_uid
    True


Restore edge cases
..................

A sample of the AT layout that is stored in another container now stays
there, and a sample that is not stored any longer is not put back:

    >>> cabinet = api.create(room, "StorageContainer", title="Cabinet",
    ...                      rows=1, columns=2)
    >>> moved_box = api.create(cabinet, "StorageSamplesContainer",
    ...                        title="Moved box", rows=2, columns=1)
    >>> other_box = api.create(cabinet, "StorageSamplesContainer",
    ...                        title="Other box", rows=1, columns=1)
    >>> sample_e = new_sample()
    >>> sample_f = new_sample()
    >>> other_box.add_object_at(sample_e, 0, 0)
    True
    >>> IAnnotations(moved_box)[ATTRIBUTE_STORAGE] = {
    ...     "Rows": 1, "Columns": 2,
    ...     "PositionsLayout": [layout_item(0, 0, sample_e),
    ...                         layout_item(0, 1, sample_f)]}
    >>> api.get_review_status(sample_f)
    'sample_received'

    >>> steps.restore_migrated_layouts(portal_setup)
    >>> moved_box.getRows(), moved_box.getColumns()
    (1, 2)
    >>> get_layout(moved_box)
    []
    >>> get_storage_sample(sample_e) == other_box
    True

A container held under a UID that no original object has takes the first
free position. A parent that was not migrated learns the restored capacity of
the child it holds:

    >>> freezer = api.create(room, "StorageContainer", title="Freezer",
    ...                      rows=1, columns=2)
    >>> shelf = api.create(freezer, "StorageContainer", title="Shelf")
    >>> freezer.has_object(shelf)
    True
    >>> unknown_box = api.create(shelf, "StorageSamplesContainer",
    ...                          title="Unknown box", rows=2, columns=2)
    >>> unknown_box.get_samples_capacity()
    4

The migration left the box out of the layout of the shelf:

    >>> shelf.remove_object(unknown_box)
    True
    >>> IAnnotations(shelf)[ATTRIBUTE_STORAGE] = {
    ...     "Rows": 1, "Columns": 3,
    ...     "PositionsLayout": [layout_item(0, 2, None, uid="1" * 32)]}
    >>> get_capacity(freezer, shelf)
    [1]

    >>> steps.restore_migrated_layouts(portal_setup)
    >>> shelf.getRows(), shelf.getColumns()
    (1, 3)
    >>> get_layout(shelf) == [(0, 0, api.get_id(unknown_box))]
    True
    >>> get_capacity(freezer, shelf)
    [6]
