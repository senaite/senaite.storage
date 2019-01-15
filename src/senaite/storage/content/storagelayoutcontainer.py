# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.Field import IntegerField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import IntegerWidget
from Products.validation.validators.ExpressionValidator import \
    ExpressionValidator
from bika.lims import api
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.idserver import renameAfterCreation
from plone.app.folder.folder import ATFolder
from senaite.storage import logger
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.interfaces import IStorageLayoutContainer, \
    IStorageSamplesContainer
from zope.interface import implements

Rows = IntegerField(
    name = "Rows",
    default = 1,
    widget = IntegerWidget(
        label = _("Rows"),
        description = _("Alphabet letters will be used to represent a row "
                        "within the container")
    ),
    validators = (
        ExpressionValidator('python: int(value) > 0'),
        ExpressionValidator('python: here.get_minimum_size()[0] <= int(value)')
    )
)

Columns = IntegerField(
    name = "Columns",
    default = 1,
    widget = IntegerWidget(
        label = _("Columns"),
        description = _("Number of positions per row. Numbers will be used to "
                        "represent a column within a row")
    ),
    validators = (
        ExpressionValidator('python: int(value) > 0'),
        ExpressionValidator('python: here.get_minimum_size()[1] <= int(value)')
    )
)

# This field is not editable and is generated automatically based on the rows,
# columns and occupied positions. It returns a list of dicts. Each dict
# represents an object stored within this container at the given 'column' and
# 'row' keys. The UID of the object is stored as a value for the key 'uid'.
# "capacity" refers to the number of samples the contained object can store
# directly or indirectly (through other child containers). "utilization" field
# refers to the number of sample the contained object actually stores directly
# or indirectly.
# The total capacity and utilization of this container is the sum of values of
# the capacity and utilization of the objects this container stores.
PositionsLayout = RecordsField(
    name = "PositionsLayout",
    visible = False,
    subfields = (
        "row",
        "column",
        "uid",
        "samples_capacity",
        "samples_utilization"),
    subfield_types = {
        "row": "int",
        "column": "int",
        "samples_capacity": "int",
        "samples_utilization": "int"}
)

schema = BikaFolderSchema.copy() + Schema((
    Rows,
    Columns,
    PositionsLayout,
))

class StorageLayoutContainer(ATFolder):
    """Base class for storage containers
    """
    implements(IStorageLayoutContainer)
    _at_rename_after_creation = True
    displayContentsTab = False
    schema = schema

    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)

    def setRows(self, value):
        self.getField('Rows').set(self, value)
        self.rebuild_layout()

    def setColumns(self, value):
        self.getField('Columns').set(self, value)
        self.rebuild_layout()

    def rebuild_layout(self):
        """Rebuilds the layout with all positions
        """
        new_layout = list()
        for num_row in range(self.getRows()):
            for num_col in range(self.getColumns()):
                new_item = {
                    "row": num_row,
                    "column": num_col,
                    "uid": "",
                    "samples_capacity": 1,
                    "samples_utilization": 0 }
                item = self.get_item_at(num_row, num_col)
                new_item = item and item.copy() or new_item
                new_layout.append(new_item)
        self.getField("PositionsLayout").set(self, new_layout)

    def setPositionsLayout(self, values):
        self.getField("PositionsLayout").set(self, values)
        self.rebuild_layout()

    def is_valid_position(self, row, column):
        """Returns whether the position defined is valid or not for this
        container's layout
        """
        col_num = api.to_int(column, default=-1)
        if col_num < 0 or col_num >= self.getColumns():
            return False
        row_num = api.to_int(row, default=-1)
        if row_num < 0 or row_num >= self.getRows():
            return False
        return True

    def get_item_at(self, row, column):
        """Returns the layout item this container contains at the given position
        """
        if not self.is_valid_position(row, column):
            return None
        row_idx = api.to_int(row)
        col_idx = api.to_int(column)
        for item in self.getPositionsLayout():
            if api.to_int(item["row"]) != row_idx:
                continue
            if api.to_int(item["column"]) != col_idx:
                continue
            return item
        return None

    def get_uid_at(self, row, column):
        """Returns a uid this container contains at the given position.
        """
        item = self.get_item_at(row, column)
        return item and item["uid"] or None

    def get_object_at(self, row, column):
        """Returns an object this container contains at the given position
        """
        uid = self.get_uid_at(row, column)
        if not api.is_uid(uid):
            return None
        return api.get_object_by_uid(uid, default=None)

    def get_object_position(self, object_brain_uid):
        """Returns the position as a tuple (row, column) of the object. If the
        object is not found, returns None
        """
        uid = api.get_uid(object_brain_uid)
        if not uid:
            return None
        els = filter(lambda el: el['uid'] == uid, self.getPositionsLayout())
        if not els:
            return None
        return (api.to_int(els[0]['row']), api.to_int(els[0]['column']))

    def has_object(self, object_brain_uid):
        """Returns if the container contains the object passed in
        """
        if self.get_object_position(object_brain_uid):
            return True
        return False

    def is_object_allowed(self, object_brain_uid):
        """Returns whether the type of object can be stored or not in this
        container. This function returns true if the object is allowed, even
        if the container already contains the object
        """
        raise NotImplementedError("Must be implemented by subclass")

    def get_layout_containers(self):
        """Returns the containers that belongs to this container and implement
        IStorageLayoutContainer
        """
        return filter(lambda obj: IStorageLayoutContainer.providedBy(obj),
                            self.objectValues())

    def get_first_empty_position(self):
        """Returns the first empty position of the layout as a tuple (row, col)
        If there are no empty positions, returns None
        """
        els = filter(lambda el: not el['uid'], self.getPositionsLayout())
        if not els:
            return None
        els = map(lambda el: (api.to_int(el['row']),
                              api.to_int(el['column'])), els) or (0,0)
        return min(els)

    def get_minimum_size(self):
        """Returns a tuple (rows, columns) that represents the minimum size this
        container can have without removing any of the objects it contains
        """
        els = filter(lambda el: el['uid'], self.getPositionsLayout())
        rows = map(lambda el: api.to_int(el['row']), els) or [0]
        cols = map(lambda el: api.to_int(el['column']), els) or [0]
        return (max(rows)+1, max(cols)+1)

    def get_capacity(self):
        """Returns the total number of positions available for this container
        """
        return self.getRows() * self.getColumns()

    def is_full(self):
        """Returns if the container is full. This is, there are no empty
        positions remaining without an object in there
        """
        return not self.get_first_empty_position()

    def remove_object(self, object_brain_uid, notify_parent=True):
        """Removes the object from the container, if in there
        """
        uid = api.get_uid(object_brain_uid)
        if not uid:
            return False
        els = filter(lambda el: el['uid'] != uid, self.getPositionsLayout())
        self.setPositionsLayout(els)

        if not notify_parent:
            return True

        # Notify the change to the parent, so it gets updated with the changes
        # regarding to capacity and utilization
        parent = api.get_object(self)
        if IStorageLayoutContainer.providedBy(parent):
            parent.update_object(self)

        return True

    def update_object(self, object_brain_uid):
        """Updates the object from the container, if in there
        """
        position = self.get_object_position(object_brain_uid)
        if not position:
            return False
        if not self.remove_object(object_brain_uid, notify_parent=False):
            return False
        return self.add_object_at(object_brain_uid, position[0], position[1])

    def can_add_object(self, object_brain_uid, row, column):
        """Returns whether the object can be added to the position
        """
        # Is the position valid?
        if not self.is_valid_position(row, column):
            return False

        # Is a valid object or a valid uid?
        uid = api.get_uid(object_brain_uid)
        if not uid:
            return False

        # If position occupied, the addition is not allowed
        if self.get_uid_at(row, column):
            return False

        # If the container already contains the object, do nothing
        if self.has_object(object_brain_uid):
            return False

        # Check if this type of object suits well with this container
        obj = api.get_object(object_brain_uid)
        if not self.is_object_allowed(obj):
            return False

        return True

    def add_object(self, object_brain_uid):
        """Adds an object to the first available position.
        """
        position = self.get_first_empty_position()
        if not position:
            return False
        return self.add_object_at(object_brain_uid, position[0], position[1])

    def add_object_at(self, object_brain_uid, row, column):
        """Adds an object to the specified position. If an object already exists
        at the given position, return False. Otherwise, return True
        """
        if not self.can_add_object(object_brain_uid, row, column):
            return False

        uid = api.get_uid(object_brain_uid)
        obj = api.get_object(object_brain_uid)

        # If the object does not implement StorageLayoutContainer, then we
        # assume the object is not a container, rather the content that needs to
        # be contained (e.g. a Sample), so we set capacity and utilization to 1
        samples_capacity = 1
        samples_utilization = 1
        if IStorageLayoutContainer.providedBy(obj):
            # This is a container, so infer the capacity and utilization
            samples_capacity = obj.get_samples_capacity()
            samples_utilization = obj.get_samples_utilization()

        row = api.to_int(row)
        column = api.to_int(column)
        layout = [{'uid': uid,
                   'row': row,
                   'column': column,
                   'samples_capacity': samples_capacity,
                   'samples_utilization': samples_utilization,}]
        for item in self.getPositionsLayout():
            if item["row"] == row and item["column"] == column:
                continue
            layout.append(item.copy())
        self.setPositionsLayout(layout)

        # Notify the change to the parent, so it gets updated with the changes
        # regarding to capacity and utilization
        parent = api.get_parent(self)
        if IStorageLayoutContainer.providedBy(parent):
            parent.update_object(self)

        return True

    def get_layout_subfield_sum(self, subfield):
        """Returns the sum of the elements stored in the layout for the subfield
        name passed in. If the value for the element is not floatable, uses 0
        """
        layout = self.getPositionsLayout()
        return sum(map(lambda el: api.to_int(el[subfield], default=0), layout))

    def get_samples_capacity(self):
        """Returns the total number of samples this container can store directly
        or indirectly through contained containers
        """
        return self.get_layout_subfield_sum(subfield="samples_capacity")

    def get_samples_utilization(self):
        """Returns the total number of samples this container actually stores,
        directly or indirectly through contained containers
        """
        return self.get_layout_subfield_sum(subfield="samples_utilization")

    def is_samples_full(self):
        """Returns whether if this container actually stores the maximum number
        of samples allowed, directly or indirectly. Note that it will return
        true if all containers this container contains are full of samples, even
        if there are still free positions for new containers
        """
        return self.get_samples_capacity() == self.get_samples_utilization()

    def reset_samples_usage(self, recursive=True):
        """Resets the sample usage values (capacity and utilization) for this
        container. It looks through all children to reset the values.
        If recursive is set to True, the function reset the samples usage for
        contained containers too.
        """
        items = map(lambda item: item["uid"], self.getPositionsLayout())
        uids = filter(api.is_uid, items)
        if not uids:
            return

        query = dict(UID=uids)
        uids_usage = {}
        for brain in api.search(query, "uid_catalog"):
            obj = api.get_object(brain)
            if not IStorageLayoutContainer.providedBy(obj):
                continue
            if recursive:
                obj.reset_samples_usage(recursive=recursive)
            uids_usage[api.get_uid(obj)] = {
                "samples_utilization": obj.get_samples_utilization(),
                "samples_capacity": obj.get_samples_capacity() }

        new_items = list()
        for layout_item in self.getPositionsLayout():
            item = layout_item.copy()
            usage = uids_usage.get(item.get("uid"), None)
            if usage:
                item.update(usage)
            new_items.append(item)
        self.setPositionsLayout(new_items)
