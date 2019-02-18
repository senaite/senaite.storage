# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.STORAGE
#
# Copyright 2019 by it's authors.

from bika.lims.api import *
from senaite.storage import logger
from senaite.storage.catalog import SENAITE_STORAGE_CATALOG
from bika.lims.utils.analysisrequest import create_analysisrequest as crar
from bika.lims import workflow as wf


def get_storage_sample(sample_obj_brain_or_uid, as_brain=False):
    """Returns the storage container the sample passed in is stored in
    """
    query = dict(portal_type="StorageSamplesContainer",
                 get_samples_uids=[get_uid(sample_obj_brain_or_uid)])
    brains = search(query, SENAITE_STORAGE_CATALOG)
    if not brains:
        return None
    if as_brain:
        return brains[0]
    return get_object(brains[0])


def create_partition_for_storage(sample_obj_brain_or_uid):
    """Creates an empty partition suitable for storage from the given sample
    If the sample passed in is a partition, generates a copy of the same
    partition without analyses set, but keeping the same parent.
    If the sample passed in is a primary sample, generates a new partition, but
    without analyses
    """
    sample = get_object(sample_obj_brain_or_uid)
    logger.info("Creating partition for storage: {}".format(get_id(sample)))

    PARTITION_SKIP_FIELDS = [
        "Analyses",
        "Attachment",
        "Client",
        "Profile",
        "Profiles",
        "RejectionReasons",
        "Remarks",
        "ResultsInterpretation",
        "ResultsInterpretationDepts",
        "Sample",
        "Template",
        "creation_date",
        "id",
        "modification_date",
        "ParentAnalysisRequest",
    ]
    primary = sample
    if sample.isPartition():
        primary = sample.getParentAnalysisRequest()

    # Set the basic fields for the Partition
    record = {
        "ParentAnalysisRequest": get_uid(primary),
    }

    # Copy all fields
    for fieldname, field in get_fields(sample).items():
        if field.type == "computed":
            logger.info("Skipping computed field {}".format(fieldname))
            continue
        if fieldname in PARTITION_SKIP_FIELDS:
            logger.info("Skipping field {}".format(fieldname))
            continue
        fieldvalue = field.get(sample)
        record[fieldname] = fieldvalue
        logger.info("Update record '{}': {}".format(
            fieldname, repr(fieldvalue)))

    client = sample.getClient()
    partition = crar(client, request={}, values=record)

    # Force status to "stored"
    wf.changeWorkflowState(partition, "bika_ar_workflow", "stored")

    # Reindex the primary AR
    primary.reindexObject(idxs=["isRootAncestor"])
    return partition
