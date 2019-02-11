from bika.lims import api
from bika.lims import workflow as wf
from senaite.storage import api as _api


def getDateStored(self):
    """Returns the date the sample was stored
    """
    return wf.getTransitionDate(self, "store") or None


def getSamplesContainer(self):
    """Returns the samples container the sample is located in
    """
    return _api.get_storage_sample(self)


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
