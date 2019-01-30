
from bika.lims import api
from senaite.storage.catalog import SENAITE_STORAGE_CATALOG


def AfterTransitionSampleEventHandler(sample, event):
    """Actions to be done after a transition for this sample takes place
    """
    if not event.transition:
        return

    if event.transition.id == "recover":
        handle_sample_recover(sample)


def handle_sample_recover(sample):
    """Removes the sample from the sample container where is stored
    """
    query = dict(portal_type="StorageSamplesContainer",
                 get_samples_uids=api.get_uid(sample))
    for brain in api.search(query, SENAITE_STORAGE_CATALOG):
        obj = api.get_object(brain)
        obj.remove_object(sample)
