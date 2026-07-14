Storage location stickers
-------------------------

Storage location objects (facilities, positions, containers and samples
containers) can be printed as barcode stickers. A dedicated
`IGetStickerTemplates` adapter offers the storage location template, and the
storage listings expose a "Print stickers" action.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t Stickers

Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from senaite.core.interfaces import IGetStickerTemplates
    >>> from senaite.storage.adapters.stickers import STORAGE_STICKER
    >>> from zope.component import getAdapters
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> storage = portal.senaite_storage

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])

Build a storage location hierarchy:

    >>> sf = api.create(storage, "StorageFacility", title="Facility")
    >>> sp = api.create(sf, "StoragePosition", title="Room A")
    >>> sc = api.create(sp, "StorageContainer", title="Freezer A")
    >>> ssc = api.create(sc, "StorageSamplesContainer",
    ...                  title="3x3 container", Rows=3, Columns=3)


Sticker adapter
...............

Each storage location type provides the storage sticker template:

    >>> def sticker_ids(context):
    ...     adapters = getAdapters((context,), IGetStickerTemplates)
    ...     ids = []
    ...     for name, adapter in adapters:
    ...         ids += [t["id"] for t in adapter(request)]
    ...     return ids

    >>> sticker_ids(sf) == [STORAGE_STICKER]
    True
    >>> sticker_ids(sp) == [STORAGE_STICKER]
    True
    >>> sticker_ids(sc) == [STORAGE_STICKER]
    True
    >>> sticker_ids(ssc) == [STORAGE_STICKER]
    True


Sticker view
............

The `@@sticker` view resolves the storage template as the selected one and
renders a barcode carrying the location id:

    >>> view = api.get_view("sticker", context=ssc, request=request)
    >>> request["items"] = api.get_uid(ssc)
    >>> view.get_selected_template() == STORAGE_STICKER
    True

    >>> templates = view.get_available_templates()
    >>> [t["id"] for t in templates] == [STORAGE_STICKER]
    True

The rendered sticker embeds the container id both as the barcode payload and
as human-readable text:

    >>> html = view.render_sticker(view.items[0])
    >>> api.get_id(ssc) in html
    True
    >>> 'class="barcode"' in html
    True


Listing action
..............

The storage listings offer a "Print stickers" action in every review state:

    >>> from senaite.storage.browser.storage.view import StorageListingView
    >>> listing = StorageListingView(storage, request)
    >>> listing.add_print_stickers_action()
    >>> actions = set()
    >>> for review_state in listing.review_states:
    ...     for transition in review_state.get("custom_transitions", []):
    ...         actions.add(transition["id"])
    >>> "print_stickers" in actions
    True

Calling it twice does not duplicate the action:

    >>> listing.add_print_stickers_action()
    >>> [t["id"] for t in listing.review_states[0]["custom_transitions"]]
    ['print_stickers']


Object action
.............

Each storage location type exposes a "Stickers preview" object action, so the
sticker can be printed directly from the object view:

    >>> portal_types = api.get_tool("portal_types")
    >>> def has_sticker_action(type_name):
    ...     fti = portal_types.getTypeInfo(type_name)
    ...     return any(action.id == "sticker_preview"
    ...                for action in fti.listActions())

    >>> all(has_sticker_action(name) for name in [
    ...     "StorageFacility", "StoragePosition",
    ...     "StorageContainer", "StorageSamplesContainer"])
    True
