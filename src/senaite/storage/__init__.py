# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

import logging

from AccessControl import allow_module
from Products.Archetypes.atapi import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.utils import ContentInit
from zope.i18nmessageid import MessageFactory

PRODUCT_NAME = "senaite.storage"
PROFILE_ID = "profile-{}:default".format(PRODUCT_NAME)

# Make senaite.storage modules importable by through-the-web
# https://docs.plone.org/develop/plone/security/sandboxing.html
# https://docs.zope.org/zope2/zdgbook/Security.html
# This allows Script python (e.g. guards from skins) to access to these modules.
# To provide access to a module inside of a package, we need to provide security
# declarations for all of the the packages and sub-packages along the path
# used to access the module. Thus, all the modules from the path passed in to
# `allow_module` will be available.
allow_module('senaite.storage.workflow.samplescontainer.guards')


# Defining a Message Factory for when this product is internationalized.
senaiteMessageFactory = MessageFactory(PRODUCT_NAME)

logger = logging.getLogger(PRODUCT_NAME)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    logger.info("*** Initializing SENAITE.STORAGE ***")

    from .content.storagerootfolder import StorageRootFolder
    from .content.storagecontainer import StorageContainer
    from .content.storagefacility import  StorageFacility
    from .content.storagesamplescontainer import StorageSamplesContainer

    types = listTypes(PRODUCT_NAME)
    content_types, constructors, ftis = process_types(types, PRODUCT_NAME)

    # Register each type with it's own Add permission
    # use ADD_CONTENT_PERMISSION as default
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: Add %s" % (PRODUCT_NAME, atype.portal_type)
        ContentInit(kind,
                    content_types=(atype,),
                    permission=AddPortalContent,
                    extra_constructors=(constructor, ),
                    fti=ftis,
                    ).initialize(context)
