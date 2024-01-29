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
# Copyright 2019-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.storage import PRODUCT_NAME
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.browser import BaseView


class DiscardSamplesView(BaseView):
    """Action URL for the sample "discard" transition
    """
    template = ViewPageTemplateFile("templates/discard_samples.pt")

    def __init__(self, context, request):
        super(DiscardSamplesView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.portal = api.get_portal()
        self.back_url = api.get_url(self.context)

    def __call__(self):
        form = self.request.form

        # form submit toggle
        submitted = form.get("submitted", False)
        discard = form.get("button_discard", False)
        cancel = form.get("button_cancel", False)

        # handle discard action
        if submitted and discard:
            reasons = form.get("reasons", [])
            comment = form.get("comment", "").strip()
            reasons.extend(comment.split("\r\n"))
            reasons = filter(None, reasons)

            # convert to a single string
            reasons = "\r\n".join(reasons)

            # strip off leading and trailing escape sequences
            reasons = reasons.strip("\n\r\t")

            if not reasons:
                return self.redirect(
                    redirect_url=self.request.getHeader("http_referer"),
                    message=_("Please specify a reason"), level="error")

            # discard the samples
            for sample in self.get_samples():
                self.discard(sample, reasons)

            return self.redirect()

        # handle cancel
        if submitted and cancel:
            return self.redirect(message=_("Discard action was cancelled"))

        return self.template()

    def get_reasons(self):
        """Returns the predefined list of reasons for discarding samples
        """
        key = "{}.discard_reasons".format(PRODUCT_NAME)
        return api.get_registry_record(key, default=True)

    def get_samples(self):
        """Returns the samples from the request UIDs
        """
        objects = self.get_objects_from_request()
        return filter(IAnalysisRequest.providedBy, objects)

    def get_samples_data(self):
        """Return a list of dicts representing the samples to be discarded
        """
        for obj in self.get_samples():
            obj = api.get_object(obj)
            yield {
                "obj": obj,
                "id": api.get_id(obj),
                "uid": api.get_uid(obj),
                "title": api.get_title(obj),
                "url": api.get_url(obj),
                "sample_type": obj.getSampleTypeTitle(),
            }

    def discard(self, sample, comment):
        """Dispatch the sample
        """
        wf = api.get_tool("portal_workflow")
        try:
            wf.doActionFor(sample, "discard", comment=comment)
            return True
        except WorkflowException:
            return False
