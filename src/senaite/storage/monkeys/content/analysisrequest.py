from bika.lims import api
from bika.lims import workflow as wf
from senaite.storage.catalog import SENAITE_STORAGE_CATALOG


def getDateStored(self):
    """Returns the date the sample was stored
    """
    return wf.getTransitionDate(self, "store") or None


def getSamplesContainer(self):
    """Returns the samples container the sample is located in
    """
    query = dict(portal_type="SamplesContainer",
                 get_samples_uids=api.get_uid(self))
    brains = api.search(query, SENAITE_STORAGE_CATALOG)
    return brains and api.get_object(brains[0]) or None


def getSamplesContainerID(self):
    """Returns the ID of the samples container the sample is located in
    """
    container = getSamplesContainer(self)
    return container and api.get_id(container) or ""


def getSamplesContainerURL(self):
    """Returns the URL of the samples container the sample is located in
    """
    container = getSamplesContainer(self)
    return container and api.get_url(container) or ""