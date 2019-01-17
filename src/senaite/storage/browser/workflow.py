# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from bika.lims import api
from bika.lims.browser.analysisrequest.workflow import \
    AnalysisRequestWorkflowAction as CoreWorkflowAction
from senaite.storage import senaiteMessageFactory as _
from senaite.storage.catalog import SENAITE_STORAGE_CATALOG
from senaite.storage import logger


def get_storage_view_url(back_url, uids):
    """Returns a well formatted url for the Storage container selector view
    """
    if isinstance(uids, basestring):
        uids = uids.split(",")
    return "{}/storage_store_samples?uids={}".format(back_url, ",".join(uids))


def get_storage_sample(sample_obj_brain_or_uid):
    """Returns the storage container the sample passed in is stored in
    """
    query = dict(portal_type="StorageSamplesContainer",
                 get_samples_uids=[api.get_uid(sample_obj_brain_or_uid)])
    brains = api.search(query, SENAITE_STORAGE_CATALOG)
    return brains and api.get_object(brains[0]) or None


def recover_sample(sample):
    """Unassings the sample from its storage container and "recover"
    """
    container = get_storage_sample(api.get_uid(sample))
    if not container:
        logger.warn("Container for Sample {} not found".format(sample.getId()))
        return False
    return container.remove_object(sample)


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
        if recover_sample(self.context):
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
            if recover_sample(sample):
                processed.append(sample.getId())

        if not processed:
            message = _("Unable to recover the samples")
            self.redirect(message=message, level="error")

        message = _("Samples recovered: {}").format(','.join(processed))
        self.redirect(message=message)
