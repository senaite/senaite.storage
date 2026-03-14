# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import workflow as wf
from bika.lims.interfaces import IAnalysisRequest
from plone.autoform import directives
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.z3cform.widgets.number import NumberWidget
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.catalog import STORAGE_CATALOG
from senaite.storage.content.storage_layout_container import \
    IStorageLayoutContainerSchema
from senaite.storage.content.storage_layout_container import \
    StorageLayoutContainer
from senaite.storage.interfaces import IStorageSamplesContainer
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant


class IStorageSamplesContainerSchema(IStorageLayoutContainerSchema):

    title = schema.TextLine(
        title=_(
            u"title_storage_samples_container_title",
            default=u"Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"title_storage_samples_container_description",
            default=u"Description"
        ),
        required=False,
    )

    managed = schema.Bool(
        title=_(
            u"title_storage_samples_container_managed",
            default=u"Managed positions"
        ),
        description=_(
            u"description_storage_samples_container_managed",
            default=u"Track samples in fixed row and column positions"
        ),
        required=False,
        default=True,
    )

    directives.widget("physical_capacity", NumberWidget)
    physical_capacity = schema.Int(
        title=_(
            u"title_storage_samples_container_physical_capacity",
            default=u"Physical capacity"
        ),
        description=_(
            u"description_storage_samples_container_physical_capacity",
            default=u"Maximum number of samples for unmanaged containers. "
                    u"Leave empty when there is no explicit limit."
        ),
        required=False,
        default=None,
    )

    directives.order_after(managed="description")
    directives.order_after(rows="managed")
    directives.order_after(columns="rows")
    directives.order_after(physical_capacity="columns")

    # hide internal fields
    directives.omitted("positions_layout")
    directives.omitted("available_positions")

    @invariant
    def validate_physical_capacity(data):
        """The physical capacity must be positive when defined."""
        value = getattr(data, "physical_capacity", None)
        if value is None:
            return
        if value <= 0:
            raise Invalid(_("Physical capacity must be greater than zero"))


@implementer(IStorageSamplesContainer, IStorageSamplesContainerSchema)
class StorageSamplesContainer(StorageLayoutContainer):
    """Container for the storage of samples
    """
    _catalogs = [STORAGE_CATALOG]

    default_samples_capacity = 1

    def Description(self):
        if self.is_managed():
            return super(StorageSamplesContainer, self).Description()
        capacity = self.get_capacity_limit()
        if capacity is None:
            return _("Unmanaged container")
        return _("Unmanaged container (capacity: {})".format(capacity))

    def getManaged(self):
        accessor = self.accessor("managed")
        value = accessor(self)
        if value is None:
            return True
        return bool(value)

    def setManaged(self, value):
        mutator = self.mutator("managed")
        mutator(self, bool(value))
        self.sync_managed_capacity()
        self.rebuild_layout()
        self.reindexObject(idxs=["is_full", "get_samples_uids"])

    Managed = property(getManaged, setManaged)

    def is_managed(self):
        return self.getManaged()

    def requires_position_tracking(self):
        return self.is_managed()

    def getPhysicalCapacity(self):
        if self.is_managed():
            return self.getRows() * self.getColumns()
        accessor = self.accessor("physical_capacity")
        value = accessor(self)
        if value in ("", None):
            return None
        return api.to_int(value, default=None)

    def setPhysicalCapacity(self, value):
        mutator = self.mutator("physical_capacity")
        if value in ("", None):
            mutator(self, None)
        else:
            mutator(self, api.to_int(value, default=None))
        self.reindexObject(idxs=["is_full"])

    PhysicalCapacity = property(getPhysicalCapacity, setPhysicalCapacity)

    def has_physical_capacity(self):
        return self.getPhysicalCapacity() is not None

    def sync_managed_capacity(self):
        """Keep physical capacity aligned with the grid for managed boxes."""
        if not self.is_managed():
            return
        mutator = self.mutator("physical_capacity")
        mutator(self, self.getRows() * self.getColumns())

    def get_capacity_limit(self):
        if self.is_managed():
            return super(StorageSamplesContainer, self).get_samples_capacity()
        return self.getPhysicalCapacity()

    def get_minimum_size(self):
        if not self.is_managed():
            return (0, 0)
        return super(StorageSamplesContainer, self).get_minimum_size()

    def setRows(self, value):
        super(StorageSamplesContainer, self).setRows(value)
        self.sync_managed_capacity()

    Rows = property(StorageLayoutContainer.getRows, setRows)

    def setColumns(self, value):
        super(StorageSamplesContainer, self).setColumns(value)
        self.sync_managed_capacity()

    Columns = property(StorageLayoutContainer.getColumns, setColumns)

    def setPositionsLayout(self, values):
        if self.is_managed():
            return super(StorageSamplesContainer, self).setPositionsLayout(values)
        mutator = self.mutator("positions_layout")
        mutator(self, values)
        self.setAvailablePositions([])

    PositionsLayout = property(StorageLayoutContainer.getPositionsLayout,
                               setPositionsLayout)

    def rebuild_layout(self):
        if self.is_managed():
            return super(StorageSamplesContainer, self).rebuild_layout()
        self.setAvailablePositions([])
        return self.getPositionsLayout()

    def get_available_positions(self):
        if not self.requires_position_tracking():
            return []
        return super(StorageSamplesContainer, self).get_available_positions()

    def get_next_unmanaged_position(self):
        """Return the next synthetic position for unmanaged containers."""
        layout = self.getPositionsLayout()
        if not layout:
            return (0, 0)
        rows = [api.to_int(item.get("row"), default=-1) for item in layout]
        return (max(rows) + 1, 0)

    def get_first_empty_position(self):
        if self.requires_position_tracking():
            return super(StorageSamplesContainer, self).get_first_empty_position()
        if self.is_full():
            return None
        return self.get_next_unmanaged_position()

    def can_add_object(self, object_brain_uid, row=None, column=None):
        if self.requires_position_tracking():
            return super(StorageSamplesContainer, self).can_add_object(
                object_brain_uid, row, column)

        uid = api.get_uid(object_brain_uid)
        if not uid:
            return False

        if self.has_object(object_brain_uid):
            return False

        if self.is_full():
            return False

        obj = api.get_object(object_brain_uid)
        if not self.is_object_allowed(obj):
            return False
        return True

    def add_object(self, object_brain_uid):
        if self.requires_position_tracking():
            return super(StorageSamplesContainer, self).add_object(
                object_brain_uid)
        position = self.get_next_unmanaged_position()
        return self.add_object_at(object_brain_uid, position[0], position[1])

    def is_object_allowed(self, object_brain_uid):
        """Returns whether the type of object can be stored or not in this
        container. This function returns true if the object is allowed, even
        if the container already contains the object
        """
        # TODO Filer by sample type, volume, etc.
        # Only objects from IAnalysisRequest are allowed
        obj = api.get_object(object_brain_uid)
        return IAnalysisRequest.providedBy(obj)

    def add_object_at(self, object_brain_uid, row, column):
        """Adds an sample to the specified position. If an object already exists
        at the given position, return False.
        """
        sample = api.get_object(object_brain_uid)
        if self.requires_position_tracking():
            if not self.can_add_object(sample, row, column):
                return False
            stored = super(StorageSamplesContainer, self).add_object_at(
                sample, row, column)
        else:
            if not self.can_add_object(sample, row, column):
                return False
            row, column = self.get_next_unmanaged_position()
            layout = list(self.getPositionsLayout())
            layout.append({
                "uid": api.get_uid(sample),
                "row": api.to_int(row),
                "column": api.to_int(column),
                "samples_capacity": 1,
                "samples_utilization": 1,
            })
            self.setPositionsLayout(layout)
            self.notify_parent()
            stored = True

        if not stored:
            return False

        # Transition the sample to "stored" state
        # TODO check if the sample has a container assigned in BeforeTransition
        # If it does not have a container assigned, change the workflow state
        # to the previous one automatically (integrity-check)
        self.reindexObject(idxs=["get_samples_uids", "is_full"])
        sample = api.get_object(sample)
        wf.doActionFor(sample, "store")
        return stored

    def remove_object(self, object_brain_uid, notify_parent=True):
        """Removes the object from the container, if in there
        """
        removed = super(StorageSamplesContainer, self).remove_object(
            object_brain_uid, notify_parent=notify_parent)
        if removed:
            self.reindexObject(idxs=["get_samples_uids", "is_full"])
        return removed

    def has_samples(self):
        """Returns whether this sample container contains samples or not
        """
        return len(self.get_samples_uids()) > 0

    def get_samples_uids(self):
        """Returns the uids of the samples this container contains
        """
        uids = map(lambda item: item.get("uid", ""), self.getPositionsLayout())
        return filter(api.is_uid, uids)

    def get_samples_capacity(self):
        if self.is_managed():
            return super(StorageSamplesContainer, self).get_samples_capacity()
        capacity = self.getPhysicalCapacity()
        if capacity is None:
            return self.get_samples_utilization()
        return capacity

    def get_samples_utilization(self):
        if self.is_managed():
            return super(StorageSamplesContainer, self).get_samples_utilization()
        return len(self.get_samples_uids())

    def is_full(self):
        if self.is_managed():
            return super(StorageSamplesContainer, self).is_full()
        capacity = self.getPhysicalCapacity()
        if capacity is None:
            return False
        return self.get_samples_utilization() >= capacity

    def is_samples_full(self):
        if self.is_managed():
            return super(StorageSamplesContainer, self).is_samples_full()
        return self.is_full()

    def get_samples(self, as_brains=False):
        samples_uids = self.get_samples_uids()
        if not samples_uids:
            return []
        query = dict(portal_type="AnalysisRequest", UID=samples_uids)
        brains = api.search(query, SAMPLE_CATALOG)
        if as_brains:
            return brains
        return map(api.get_object, brains)

    # TODO Finish this (index and searches are still missing)
    def get_sample_types_uids(self):
        """Returns the uids of the samples types of the samples this container
        contains, if any. This is mostly used for suggest searches with
        ZCTextIndex, that gives a higher score when the term is found more than
        once. Hence the list may contain duplicates
        """
        samples_uids = self.get_samples_uids()
        if not samples_uids:
            return []
        query = dict(UID=samples_uids)
        brains = api.search(query, SAMPLE_CATALOG)
        return map(lambda brain: brain.getSampleTypeUID, brains)
