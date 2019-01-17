# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from bika.lims.browser.analysisrequest.workflow import \
    AnalysisRequestWorkflowAction as CoreWorkflowAction
from bika.lims.interfaces import IAnalysisRequest
from senaite.storage import logger
from senaite.storage import senaiteMessageFactory as _
from bika.lims import api


def get_storage_view_url(back_url, uids):
    """Returns a well formatted url for the Storage container selector view
    """
    if isinstance(uids, basestring):
        uids = uids.split(",")
    return "{}/storage_store_sample?uids={}".format(back_url, ",".join(uids))


class AnalysisRequestWorkflowAction(CoreWorkflowAction):
    """Actions taken in Analysis Request context
    """

    def workflow_action_store(self):
        """Function called when transition "stored" is fired from the Analysis
        Request view. Redirects the user to the Storage container selector
        """
        url = get_storage_view_url(self.back_url, api.get_uid(self.context))
        self.redirect(redirect_url=url)


class AnalysisRequestsWorkflowAction(CoreWorkflowAction):
    """Actions taken in Analysis Requests listings context
    """

    def workflow_action_store(self):
        """Function called when transition "stored" is fired from an Analysis
        Requests listing view, in which 0 or more Analysis Request have been
        selected. Redirects the user to the Storage container selector
        """
        uids = self.get_selected_uids()
        if not uids:
            self.redirect(message=_("No items selected"), level="error")

        url = get_storage_view_url(self.back_url, uids)
        self.redirect(redirect_url=url)
