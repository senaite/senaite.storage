from senaite.core.listing import utils
from senaite.core.listing.interfaces import IListingView, IListingViewAdapter
from senaite.storage import senaiteMessageFactory as _
from zope.component import adapts
from zope.interface import implements
from bika.lims import api


class AnalysisRequestsListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        # Add stored review state
        print_stickers = {
            "id": "print_stickers",
            "title": _("Print stickers"),
            "url": "workflow_action?action=print_stickers"
        }
        base_column_ids = self.listing.columns.keys()
        hide = ["getDateVerified", "getDatePublished"]
        columns = filter(lambda col: col not in hide, base_column_ids)
        stored = {
            "id": "stored",
            "title": _("Stored"),
            "contentFilter": {
                "review_state": ("stored",),
                "sort_on": "created",
                "sort_order": "descending",
            },
            "transitions": [],
            "custom_transitions": [print_stickers],
            "columns": columns,
        }
        utils.add_review_state(self.listing, stored, after="published")

        # Add the column Date Stored to the "stored" review state
        column_values = {
            "title": _("Date stored"),
            "index": "getDateStored",
            "attr": "getId",
            "toggle": True}
        utils.add_column(self.listing, "getDateStored", column_values,
                         after="getDateReceived", review_states=("stored",))

        # Add Samples Container column, but only if the current user logged in
        # is not a client contact
        if not api.get_current_client():
            column_values = {
                "title": _("Storage"),
                "attr": "getSamplesContainerID",
                "replace_url": "getSamplesContainerURL",
                "toggle": True
            }
            utils.add_column(self.listing, "getSamplesContainer", column_values,
                             after="getDateStored", review_states=("stored", ))

    def folder_item(self, obj, item, index):
        listing = self.listing
        item["getDateStored"] = ""
        date_stored = obj.getDateStored
        if date_stored:
            item["getDateStored"] = listing.ulocalized_time(date_stored,
                                                            long_format=1)
        return item
