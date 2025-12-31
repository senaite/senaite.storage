Storage Navigation Bar Visibility
==================================

This test ensures that the Storage folder is visible in the navigation bar
after installation, in accordance with the new sidebar navigation system
introduced in senaite.core.

Running this test from the buildout directory:

    bin/test -m senaite.storage -t StorageNavigation


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_senaite_setup()
    >>> storage = portal.senaite_storage

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])


Storage Folder Navigation Visibility
-------------------------------------

After installation, the Storage folder should be visible in the navigation bar.
This is configured through two mechanisms:

1. The portal type "StorageRootFolder" should NOT be in SENAITE Setup's sidebar_skip_types
   (types in this list are excluded from the sidebar):

    >>> sidebar_skip_types = setup.getSidebarSkipTypes()
    >>> sidebar_skip_types is not None
    True
    >>> "StorageRootFolder" not in sidebar_skip_types
    True

2. Since the storage folder is a root folder (direct child of portal), its ID
   should be in SENAITE Setup's sidebar_folders:

    >>> sidebar_folders = setup.getSidebarFolders()
    >>> sidebar_folders is not None
    True
    >>> "senaite_storage" in sidebar_folders
    True


Verify Storage Folder Properties
---------------------------------

The storage folder should exist and be properly configured:

    >>> storage is not None
    True

    >>> api.get_portal_type(storage)
    'StorageRootFolder'

    >>> api.get_id(storage)
    'senaite_storage'

    >>> storage.Title()
    'Sample storage'

The storage folder should be a direct child of the portal:

    >>> api.get_parent(storage) == portal
    True
