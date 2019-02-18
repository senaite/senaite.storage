#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from bika.lims.browser.workflow import RequestContextAware
from bika.lims.interfaces import IWorkflowActionUIDsAdapter
from zope.component.interfaces import implements


class WorkflowActionAddSamplesAdapter(RequestContextAware):
    """Adapter in charge of "add samples" action
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        """Redirects the user to the Samples selector view
        """
        url = "{}/storage_store_container?uids={}".format(self.back_url,
                                                          ",".join(uids))
        return self.redirect(redirect_url=url)
