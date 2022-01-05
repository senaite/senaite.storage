# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE.
#
# SENAITE.STORAGE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2019-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

import logging

from AccessControl import allow_module
from bika.lims.api import get_request
from Products.Archetypes.atapi import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.utils import ContentInit
from senaite.storage import permissions
from senaite.storage.config import PRODUCT_NAME
from senaite.storage.interfaces import ISenaiteStorageLayer
from zope.i18nmessageid import MessageFactory

# Make senaite.storage modules importable by through-the-web
# https://docs.plone.org/develop/plone/security/sandboxing.html
# https://docs.zope.org/zope2/zdgbook/Security.html
# This allows Script python (e.g. guards from skins) to access to these
# modules. To provide access to a module inside of a package, we need to
# provide security declarations for all of the the packages and sub-packages
# along the path used to access the module. Thus, all the modules from the path
# passed in to `allow_module` will be available.
allow_module("senaite.storage.workflow.sample.guards")
allow_module("senaite.storage.workflow.samplescontainer.guards")
allow_module("senaite.storage.workflow.storage.guards")

# Defining a Message Factory for when this product is internationalized.
senaiteMessageFactory = MessageFactory(PRODUCT_NAME)

logger = logging.getLogger(PRODUCT_NAME)


def is_installed():
    """Returns whether the product is installed or not
    """
    request = get_request()
    return ISenaiteStorageLayer.providedBy(request)


def check_installed(default_return):
    """Decorator to prevent the function to be called if product not installed
    :param default_return: value to return if not installed
    """
    def is_installed_decorator(func):
        def wrapper(*args, **kwargs):
            if not is_installed():
                return default_return
            return func(*args, **kwargs)
        return wrapper
    return is_installed_decorator


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    logger.info("*** Initializing SENAITE.STORAGE ***")

    from .content.storagerootfolder import StorageRootFolder  # noqa
    from .content.storagecontainer import StorageContainer  # noqa
    from .content.storagefacility import StorageFacility  # noqa
    from .content.storagesamplescontainer import StorageSamplesContainer  # noqa

    types = listTypes(PRODUCT_NAME)
    content_types, constructors, ftis = process_types(types, PRODUCT_NAME)

    # Register each type with it's own Add permission
    # use ADD_CONTENT_PERMISSION as default
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: Add %s" % (PRODUCT_NAME, atype.portal_type)
        perm_name = "Add{}".format(atype.portal_type)
        perm = getattr(permissions, perm_name, AddPortalContent)
        ContentInit(kind,
                    content_types=(atype,),
                    permission=perm,
                    extra_constructors=(constructor, ),
                    fti=ftis,
                    ).initialize(context)
