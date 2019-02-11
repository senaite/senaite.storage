# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from bika.lims import api
from bika.lims import workflow as wf
from bika.lims.browser.analysisrequest.workflow import \
    AnalysisRequestWorkflowAction as CoreWorkflowAction
from senaite.storage import senaiteMessageFactory as _


def get_storage_view_url(back_url, uids):
    """Returns a well formatted url for the Storage container selector view
    """
    if isinstance(uids, basestring):
        uids = uids.split(",")
    return "{}/storage_store_samples?uids={}".format(back_url, ",".join(uids))


class AnalysisRequestWorkflowAction(CoreWorkflowAction):
    """Actions taken in Analysis Request context
    """

    def workflow_action_store(self):
        """Function called when transition "stored" is fired from the Analysis
        Request view. Redirects the user to the Storage container selector
        """
        url = get_storage_view_url(self.back_url, api.get_uid(self.context))
        self.redirect(redirect_url=url)

    def workflow_action_recover(self):
        """Function called when transition "recover" is fired from the Analysis
        Request view
        """
        success = wf.doActionFor(self.context, "recover")
        if success[0]:
            self.redirect(message=_("Sample recovered"))
        self.redirect(message=_("Cannot recover the sample"), level="error")


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

    def workflow_action_recover(self):
        """Function called when transition "recover" is fired from an Analysis
        Requests listing view, in which 0 or more Analysis Request have been
        selected.
        """
        uids = self.get_selected_uids()
        if not uids:
            self.redirect(message=_("No items selected"), level="error")

        processed = []
        for sample_uid in uids:
            sample = api.get_object(sample_uid)
            success = wf.doActionFor(sample, "recover")
            if success[0]:
                processed.append(api.get_id(sample))

        if not processed:
            message = _("Unable to recover the samples")
            self.redirect(message=message, level="error")

        message = _("Samples recovered: {}").format(','.join(processed))
        self.redirect(message=message)
