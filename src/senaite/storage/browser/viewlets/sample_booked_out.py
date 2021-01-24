# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.browser import ulocalized_time
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SampleBookedOutViewlet(ViewletBase):
    """Print a viewlet showing the WF history comment
    """
    template = ViewPageTemplateFile("templates/sample_booked_out_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        super(SampleBookedOutViewlet, self).__init__(
            context, request, view, manager=manager)
        self.context = context
        self.request = request
        self.view = view

    def is_booked_out(self):
        """Returns whether the current sample is booked out
        """
        return api.get_review_status(self.context) == "booked_out"

    def get_state_info(self):
        """Returns the WF state information
        """
        actor = self.context.getBookOutActor()
        user = api.user.get_user(actor)
        if user:
            actor = user.getProperty("fullname", actor)
        date = self.context.getDateBookedOut()
        reason = self.context.getBookOutReason()

        return {
            "actor": actor,
            "date": date,
            "reason": reason,
        }

    def index(self):
        if self.is_booked_out():
            return ""
        return self.template()

    def ulocalized_time(self, time, long_format=None, time_only=None):
        return ulocalized_time(time, long_format, time_only,
                               context=self.context, request=self.request)
