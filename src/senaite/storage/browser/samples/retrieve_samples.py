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

import six

from bika.lims import api
from bika.lims import workflow as wf
from bika.lims.browser import BrowserView
from bika.lims.browser import ulocalized_time
from plone.memoize import view
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.storage import _
from senaite.storage import api as _api
from senaite.storage import logger


class RetrieveSamplesView(BrowserView):
    """View that renders the retrieve reason selection form before
    recovering samples from storage
    """
    template = ViewPageTemplateFile("templates/retrieve_samples.pt")

    def __init__(self, context, request):
        super(RetrieveSamplesView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.back_url = self.context.absolute_url()

    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)

        # Buttons
        form_continue = form.get("button_continue", False)
        form_cancel = form.get("button_cancel", False)

        # Get the objects from request
        samples = self.get_samples_from_request()

        # No Samples selected
        if not samples:
            return self.redirect(message=_(u"No items selected"),
                                 level="warning")

        # group samples by uid
        by_uid = dict((api.get_uid(s), s) for s in samples)

        # Handle retrieve transition
        if form_submitted and form_continue:
            logger.info("*** RETRIEVE SAMPLES ***")
            reasons = _api.get_retrieve_reasons()
            reason_required = _api.is_retrieve_reason_required()
            processed = []

            for sample_uid in form.get("samples", []):
                sample = by_uid.get(sample_uid)
                if not sample:
                    continue

                # get the reason, if any
                record = form.get(sample_uid) or {}
                reason = record.get("reason", None)
                if reason == "__other__":
                    reason = record.get("other_reason")
                    if not reason:
                        msg = _(u"Please type the reason in the text field")
                        self.add_status_message(msg, "error")
                        return self.template()

                elif not reason and reason_required and reasons:
                    msg = _(u"Please select a retrieve reason")
                    self.add_status_message(msg, "error")
                    return self.template()

                # set the retrieve reason
                if reason:
                    sample.setRetrieveReason(reason)

                # recover the sample
                wf.doActionFor(sample, "recover")
                processed.append(sample)

            if not processed:
                return self.redirect(
                    message=_(u"No samples were retrieved"))

            message = _(u"Retrieved ${count} samples: ${ids}",
                        mapping={
                            "count": str(len(processed)),
                            "ids": ", ".join(map(api.get_id, processed)),
                        })
            return self.redirect(message=message)

        # Handle cancel
        if form_submitted and form_cancel:
            logger.info("*** CANCEL RETRIEVE ***")
            return self.redirect(message=_(u"Retrieve cancelled"))

        return self.template()

    @view.memoize
    def get_samples_from_request(self):
        """Returns a list of objects coming from the "uids" request parameter
        """
        uids = self.request.form.get("uids", "")
        if isinstance(uids, six.string_types):
            uids = uids.split(",")

        uids = list(set(uids))
        if not uids:
            return []

        # filter those samples for which the "recover" transition is allowed
        query = dict(portal_type="AnalysisRequest", UID=uids)
        samples = []
        for brain in api.search(query, SAMPLE_CATALOG):
            sample = api.get_object(brain)
            if wf.isTransitionAllowed(sample, "recover"):
                samples.append(sample)

        return samples

    def get_retrieve_reasons(self):
        """Returns the list of predefined retrieve reasons
        """
        return _api.get_retrieve_reasons()

    def is_reason_required(self):
        """Returns whether selecting a reason is mandatory
        """
        return _api.is_retrieve_reason_required()

    def get_samples_data(self):
        """Returns a list of Samples data (dictionary)
        """
        for obj in self.get_samples_from_request():
            sample_type = obj.getSampleType()
            yield {
                "obj": obj,
                "id": api.get_id(obj),
                "uid": api.get_uid(obj),
                "title": api.get_title(obj),
                "path": api.get_path(obj),
                "url": api.get_url(obj),
                "sample_type": api.get_title(sample_type),
                "client_title": obj.getClientTitle(),
                "date": ulocalized_time(
                    obj.created(), long_format=True,
                    context=obj, request=self.request),
            }

    def redirect(self, redirect_url=None, message=None, level="info"):
        """Redirect with a message
        """
        if redirect_url is None:
            redirect_url = self.back_url
        if message is not None:
            self.add_status_message(message, level)
        return self.request.response.redirect(redirect_url)

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)
