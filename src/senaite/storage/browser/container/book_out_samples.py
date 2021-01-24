# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.storage import logger
from senaite.storage.interfaces import IStorageSamplesContainer
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.browser import BaseView


class BookOutSamplesView(BaseView):
    """Store Container View. Allows to store samples in preselected containers
    """
    template = ViewPageTemplateFile("templates/book_out_samples.pt")
    action = "storage_book_out_samples"

    def __init__(self, context, request):
        super(BookOutSamplesView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.portal = api.get_portal()
        self.back_url = api.get_url(self.context)

    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)
        form_book_out = form.get("button_book_out", False)
        form_cancel = form.get("button_cancel", False)

        # Handle book out
        if form_submitted and form_book_out:
            logger.info("*** BOOK OUT ***")
            comment = form.get("comment", "")
            if not comment:
                return self.redirect(
                    redirect_url=self.request.getHeader("http_referer"),
                    message=_("Please specify a reason"), level="error")
            samples = self.get_objects()
            wf = api.get_tool("portal_workflow")
            for sample in samples:
                wf.doActionFor(sample, "book_out", comment=comment)
            return self.redirect()

        # Handle cancel
        if form_submitted and form_cancel:
            return self.redirect(message=_("Cancelled"))
        return self.template()

    def get_objects(self):
        """Get the objects to be moved
        """
        if IAnalysisRequest.providedBy(self.context):
            return [self.context]

        # fetch objects from request
        objs = self.get_objects_from_request()
        samples = []
        for obj in objs:
            if IStorageSamplesContainer.providedBy(obj):
                samples.extend(obj.get_samples())

        return list(set(samples))

    def get_title(self, obj):
        """Return the object title as unicode
        """
        title = api.get_title(obj)
        return api.safe_unicode(title)

    def get_samples_data(self):
        """Returns a list of containers that can be moved
        """
        for obj in self.get_objects():
            obj = api.get_object(obj)
            yield {
                "obj": obj,
                "id": api.get_id(obj),
                "uid": api.get_uid(obj),
                "title": self.get_title(obj),
                "url": api.get_url(obj),
            }
