# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE.
#
# SENAITE.STORAGE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2019-2026 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from senaite.storage.tests.base import SimpleTestCase

ADDRESS = [{"type": "physical", "address": "1 Lab Road", "city": "Houston",
            "zip": "77030", "country": "US"}]


class TestLayoutValidation(SimpleTestCase):
    """A layout container passes the full validation of its schema

    The JSON API validates the whole object on creation. The layout
    fields are computed and hold plain dicts and byte strings, so they
    must not take part in that validation.
    """

    def setUp(self):
        super(TestLayoutValidation, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.facility = api.create(self.portal.senaite_storage,
                                   "StorageFacility", title="Facility",
                                   address=ADDRESS)

    def create_container(self, portal_type, parent, title):
        obj = api.create(parent, portal_type, title=title)
        obj.setRows(3)
        obj.setColumns(3)
        return obj

    def assert_valid(self, obj):
        errors = api.validate(obj)
        self.assertNotIn("positions_layout", errors)
        self.assertNotIn("available_positions", errors)

    def test_storage_container(self):
        freezer = self.create_container("StorageContainer", self.facility,
                                        "Freezer")
        self.assertEqual(len(freezer.getPositionsLayout()), 9)
        self.assertEqual(len(freezer.getAvailablePositions()), 9)
        self.assert_valid(freezer)

    def test_samples_container(self):
        freezer = self.create_container("StorageContainer", self.facility,
                                        "Freezer")
        box = self.create_container("StorageSamplesContainer", freezer,
                                    "Box")
        self.assertEqual(len(box.getPositionsLayout()), 9)
        self.assert_valid(box)

    def test_layout_setter(self):
        freezer = self.create_container("StorageContainer", self.facility,
                                        "Freezer")
        freezer.setPositionsLayout([])
        # rebuild_layout restores the positions from rows and columns
        self.assertEqual(len(freezer.getPositionsLayout()), 9)
