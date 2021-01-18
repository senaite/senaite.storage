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
# Copyright 2019-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from senaite.storage import logger
from senaite.storage import senaiteMessageFactory as _s

from senaite.storage.browser import BaseView


class StoreSamplesView(BaseView):
    """Store Samples view. Allows to store preselected samples to containers
    """
    template = ViewPageTemplateFile("templates/store_samples.pt")

    def __init__(self, context, request):
        super(StoreSamplesView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.back_url = self.context.absolute_url()

    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)
        form_store = form.get("button_store", False)
        form_cancel = form.get("button_cancel", False)

        objs = self.get_objects_from_request()

        # No items selected
        if not objs:
            return self.redirect(message=_("No items selected"),
                                 level="warning")

        # Handle store
        if form_submitted and form_store:
            samples = []
            for sample in form.get("samples", []):
                sample_uid = sample.get("uid")
                container_uid = sample.get("container_uid")
                alpha_position = sample.get("container_position")
                if not sample_uid or not container_uid or not alpha_position:
                    continue

                sample_obj = self.get_object_by_uid(sample_uid)
                container = self.get_object_by_uid(container_uid)
                logger.info("Storing sample {} in {}".format(sample_obj.getId(),
                                                             container.getId()))
                # Store
                position = container.alpha_to_position(alpha_position)
                stored = container.add_object_at(sample_obj, position[0],
                                                 position[1])
                if stored:
                    stored = container.get_object_at(position[0], position[1])
                    samples.append(stored)

            message = _s("Stored {} samples: {}".format(
                len(samples), ", ".join(map(api.get_title, samples))))
            return self.redirect(message=message)

        # Handle cancel
        if form_submitted and form_cancel:
            return self.redirect(message=_s("Sample storing canceled"))

        return self.template()

    def get_samples_data(self):
        """Returns a list of AR data
        """
        for obj in self.get_objects_from_request():
            obj = api.get_object(obj)
            yield {
                "obj": obj,
                "id": api.get_id(obj),
                "uid": api.get_uid(obj),
                "title": api.get_title(obj),
                "path": api.get_path(obj),
                "url": api.get_url(obj),
                "sample_type": api.get_title(obj.getSampleType())
            }
