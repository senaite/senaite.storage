# -*- coding: utf-8 -*-

from bika.lims.interfaces import IDoNotSupportSnapshots
from plone.supermodel import model
from senaite.core.content.base import Container
from senaite.core.interfaces import IHideActionsMenu
from senaite.storage.interfaces import IStorageRootFolder
from zope.interface import implementer


class IStorageRootFolderSchema(model.Schema):
    """Schema interface
    """


@implementer(IStorageRootFolder, IStorageRootFolderSchema,
             IDoNotSupportSnapshots, IHideActionsMenu)
class StorageRootFolder(Container):
    """The storage root container
    """
