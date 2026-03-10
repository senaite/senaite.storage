Retention Period
----------------

Laboratories can configure retention rules that assign default storage
retention periods based on analysis service and/or result criteria. When
storing a sample, the system computes and stores the retention expiry date.

Running this test from the buildout directory:

    bin/test -t RetentionPeriod

Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.storage import api as storage_api

Functional Helpers:

    >>> def new_sample(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': sampletype.UID()}
    ...     uids = map(api.get_uid, services)
    ...     return create_analysisrequest(client, request, values, uids)

    >>> def set_retention_rules(rules):
    ...     key = "senaite.storage.retention_period_rules"
    ...     ploneapi.portal.set_registry_record(key, rules)

    >>> def get_retention_rules():
    ...     key = "senaite.storage.retention_period_rules"
    ...     return ploneapi.portal.get_registry_record(key)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bika_setup = portal.bika_setup
    >>> storage = portal.senaite_storage

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

Create baseline objects:

    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> labcontact = api.create(bika_setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())

Setup storage structure:

    >>> sf = api.create(storage, "StorageFacility", title="Storage facility")
    >>> sp = api.create(sf, "StoragePosition", title="Room A")
    >>> sc = api.create(sp, "StorageContainer", title="Freezer A")
    >>> ssc = api.create(sc, "StorageSamplesContainer", title="3x3 container", Rows=3, Columns=3)


No rules configured
...................

When no retention rules are configured, ``get_retention_rules`` returns an
empty list:

    >>> storage_api.get_retention_rules()
    []

And ``get_default_retention_period`` returns None for any sample:

    >>> sample1 = new_sample([Cu, Fe])
    >>> do_action_for(sample1, "receive")
    (...)
    >>> storage_api.get_default_retention_period(sample1) is None
    True

The monkey-patched method on the sample itself also returns None:

    >>> sample1.getDefaultStorageRetentionPeriod() is None
    True


Configuring retention rules
...........................

Add a general rule for Copper (any result, 30 days):

    >>> Cu_uid = api.get_uid(Cu)
    >>> set_retention_rules([
    ...     {"service": Cu_uid, "result": u"", "retention_days": 30},
    ... ])

Verify the rule is stored:

    >>> rules = storage_api.get_retention_rules()
    >>> len(rules)
    1
    >>> rules[0]["service"] == Cu_uid
    True
    >>> rules[0]["retention_days"]
    30

The sample with Cu now gets a default retention of 30 days:

    >>> storage_api.get_default_retention_period(sample1)
    30


General rule matching
.....................

A general rule (empty result) matches any result for the given service. The
rule for Copper matches regardless of the analysis result:

    >>> storage_api.get_default_retention_period(sample1)
    30

Add a second general rule for Iron with a longer period:

    >>> Fe_uid = api.get_uid(Fe)
    >>> set_retention_rules([
    ...     {"service": Cu_uid, "result": u"", "retention_days": 30},
    ...     {"service": Fe_uid, "result": u"", "retention_days": 60},
    ... ])

When multiple general rules match, the longest retention period wins:

    >>> storage_api.get_default_retention_period(sample1)
    60

A sample without matching services returns None:

    >>> sample2 = new_sample([Au])
    >>> do_action_for(sample2, "receive")
    (...)
    >>> storage_api.get_default_retention_period(sample2) is None
    True


Specific rules (with result) take priority
..........................................

Add a specific rule for Copper with result "10" (90 days) alongside the
general rules:

    >>> set_retention_rules([
    ...     {"service": Cu_uid, "result": u"", "retention_days": 30},
    ...     {"service": Fe_uid, "result": u"", "retention_days": 60},
    ...     {"service": Cu_uid, "result": u"10", "retention_days": 90},
    ... ])

Without any results submitted, only general rules match:

    >>> storage_api.get_default_retention_period(sample1)
    60

Submit a matching result for Copper ("10"):

    >>> analyses = sample1.getAnalyses(full_objects=True)
    >>> cu_analysis = [a for a in analyses if a.getKeyword() == "Cu"][0]
    >>> cu_analysis.setResult("10")

Now the specific rule (90 days) takes priority over the general rules:

    >>> storage_api.get_default_retention_period(sample1)
    90

Submit a non-matching result:

    >>> cu_analysis.setResult("5")

Specific rule no longer matches, so fallback to general rules (60 days from
the Iron general rule):

    >>> storage_api.get_default_retention_period(sample1)
    60

Reset the result for subsequent tests:

    >>> cu_analysis.setResult("")


Multiple specific rules
.......................

When multiple specific rules match, the longest retention period wins:

    >>> set_retention_rules([
    ...     {"service": Cu_uid, "result": u"10", "retention_days": 90},
    ...     {"service": Fe_uid, "result": u"20", "retention_days": 120},
    ... ])

    >>> cu_analysis.setResult("10")
    >>> fe_analysis = [a for a in analyses if a.getKeyword() == "Fe"][0]
    >>> fe_analysis.setResult("20")

    >>> storage_api.get_default_retention_period(sample1)
    120

If only one specific rule matches:

    >>> fe_analysis.setResult("999")
    >>> storage_api.get_default_retention_period(sample1)
    90


Multiselect result matching
...........................

For services with ``multiselect`` or ``multichoice`` result types the
analysis result is stored as a JSON array (e.g. ``'["1"]'``). Retention
rules still specify a **single** value to match, and a rule matches if
that value is contained in the result array.

Create a multiselect service with two options:

    >>> Ms = api.create(
    ...     bika_setup.bika_analysisservices,
    ...     "AnalysisService",
    ...     title="Pathogen",
    ...     Keyword="Pa",
    ...     Price="10",
    ...     Category=category.UID(),
    ...     ResultType="multiselect",
    ...     ResultOptions=[
    ...         {"ResultValue": "1", "ResultText": "Positive"},
    ...         {"ResultValue": "0", "ResultText": "Negative"},
    ...     ])
    >>> Ms_uid = api.get_uid(Ms)

Create a sample that includes the multiselect service:

    >>> sample_ms = new_sample([Ms])
    >>> do_action_for(sample_ms, "receive")
    (...)

Configure a specific rule for the ``Positive`` result (value ``"1"``):

    >>> set_retention_rules([
    ...     {"service": Ms_uid, "result": u"1", "retention_days": 90},
    ... ])

With no result submitted the specific rule does not match:

    >>> storage_api.get_default_retention_period(sample_ms) is None
    True

Submit a multiselect result containing only ``Positive`` (value ``"1"``).
Passing a list lets SENAITE's ``setResult`` handle the JSON serialisation:

    >>> ms_analyses = sample_ms.getAnalyses(full_objects=True)
    >>> ms_analysis = [a for a in ms_analyses
    ...                if a.getKeyword() == "Pa"][0]
    >>> ms_analysis.setResult(["1"])

The specific rule now matches:

    >>> storage_api.get_default_retention_period(sample_ms)
    90

A result that does not include the matching value does not trigger the
rule:

    >>> ms_analysis.setResult(["0"])
    >>> storage_api.get_default_retention_period(sample_ms) is None
    True

A result with multiple selected values matches if one of them equals the
rule value:

    >>> ms_analysis.setResult(["0", "1"])
    >>> storage_api.get_default_retention_period(sample_ms)
    90

Reset for subsequent tests:

    >>> ms_analysis.setResult("")
    >>> set_retention_rules([])


Storing expiry date on samples
..............................

Reset to a simple general rule for Copper and clear previous results:

    >>> cu_analysis.setResult("")
    >>> fe_analysis.setResult("")
    >>> set_retention_rules([
    ...     {"service": Cu_uid, "result": u"", "retention_days": 30},
    ... ])

Before storing, the sample has no expiry date:

    >>> sample1.getStorageExpiryDate() is None
    True

Store the sample and set the expiry date (as the store views do):

    >>> ssc.add_object_at(sample1, 0, 0)
    True

    >>> api.get_workflow_status_of(sample1)
    'stored'

Compute and set the expiry date based on retention days:

    >>> retention_days = storage_api.get_default_retention_period(sample1)
    >>> retention_days
    30

    >>> expiry = DateTime() + retention_days
    >>> sample1.setStorageExpiryDate(expiry)

The expiry date is now stored on the sample:

    >>> stored_expiry = sample1.getStorageExpiryDate()
    >>> stored_expiry is not None
    True

The expiry date is approximately 30 days from now:

    >>> days_diff = int(round(stored_expiry - DateTime()))
    >>> days_diff
    30


Setting expiry date to None
............................

A sample can be stored without an expiry date:

    >>> sample3 = new_sample([Au])
    >>> do_action_for(sample3, "receive")
    (...)
    >>> ssc.add_object_at(sample3, 0, 1)
    True
    >>> sample3.setStorageExpiryDate(None)
    >>> sample3.getStorageExpiryDate() is None
    True


Retrieval clears the expiry date
.................................

When a stored sample is retrieved, the expiry date is cleared:

    >>> sample1.getStorageExpiryDate() is not None
    True

    >>> do_action_for(sample1, "recover")
    (...)

    >>> api.get_workflow_status_of(sample1)
    'sample_received'

    >>> sample1.getStorageExpiryDate() is None
    True

The sample is no longer in the container:

    >>> ssc.get_object_at(0, 0) is None
    True


Re-storing with updated rules
..............................

Rules can be changed between store/retrieve cycles. Store the sample again
with a different retention period:

    >>> set_retention_rules([
    ...     {"service": Cu_uid, "result": u"", "retention_days": 7},
    ... ])

    >>> storage_api.get_default_retention_period(sample1)
    7

    >>> ssc.add_object_at(sample1, 0, 0)
    True
    >>> expiry = DateTime() + 7
    >>> sample1.setStorageExpiryDate(expiry)

    >>> days_diff = int(round(sample1.getStorageExpiryDate() - DateTime()))
    >>> days_diff
    7

Retrieve again and verify cleanup:

    >>> do_action_for(sample1, "recover")
    (...)
    >>> sample1.getStorageExpiryDate() is None
    True


Warning days before expiration
..............................

The control panel setting ``warning_days_before_expiration`` controls how many
days before the expiry date a sample should be flagged as approaching
expiration. The default value is 5:

    >>> storage_api.get_warning_days_before_expiration()
    5

The value can be changed through the registry:

    >>> def set_warning_days(days):
    ...     key = "senaite.storage.warning_days_before_expiration"
    ...     ploneapi.portal.set_registry_record(key, days)

    >>> set_warning_days(10)
    >>> storage_api.get_warning_days_before_expiration()
    10

Reset to default for subsequent tests:

    >>> set_warning_days(5)


Retention expiration check
..........................

The ``is_retention_expired`` function checks whether a sample's retention
period has expired. It returns ``None`` if the sample has no expiry date:

    >>> sample1.getStorageExpiryDate() is None
    True
    >>> storage_api.is_retention_expired(sample1) is None
    True

Store the sample and set an expiry date 30 days from now:

    >>> set_retention_rules([
    ...     {"service": Cu_uid, "result": u"", "retention_days": 30},
    ... ])
    >>> ssc.add_object_at(sample1, 0, 0)
    True
    >>> expiry = DateTime() + 30
    >>> sample1.setStorageExpiryDate(expiry)

The retention is not expired (expiry is 30 days from now):

    >>> storage_api.is_retention_expired(sample1)
    False

Check against a specific date in the future (31 days from now):

    >>> future_date = DateTime() + 31
    >>> storage_api.is_retention_expired(sample1, on_date=future_date)
    True

Check against a specific date before the expiry (29 days from now):

    >>> before_date = DateTime() + 29
    >>> storage_api.is_retention_expired(sample1, on_date=before_date)
    False

Set the expiry date in the past to simulate an expired retention:

    >>> sample1.setStorageExpiryDate(DateTime() - 1)
    >>> storage_api.is_retention_expired(sample1)
    True


Approaching expiration check
.............................

The ``is_retention_approaching_expiration`` function checks whether a sample's
retention period is approaching expiration within the given number of days.

Set the expiry date to 3 days from now:

    >>> sample1.setStorageExpiryDate(DateTime() + 3)

With the default warning threshold of 5 days, the sample is approaching
expiration (3 days < 5 days threshold):

    >>> storage_api.is_retention_approaching_expiration(sample1)
    True

With a custom threshold of 2 days, the sample is NOT approaching expiration
(3 days > 2 days threshold):

    >>> storage_api.is_retention_approaching_expiration(sample1, days=2)
    False

A sample with an expiry date far in the future is not approaching expiration:

    >>> sample1.setStorageExpiryDate(DateTime() + 30)
    >>> storage_api.is_retention_approaching_expiration(sample1)
    False

An already expired sample is also considered as approaching expiration (since
``is_retention_approaching_expiration`` delegates to ``is_retention_expired``
with a future date offset):

    >>> sample1.setStorageExpiryDate(DateTime() - 1)
    >>> storage_api.is_retention_approaching_expiration(sample1)
    True

A sample without an expiry date returns None:

    >>> sample1.setStorageExpiryDate(None)
    >>> storage_api.is_retention_approaching_expiration(sample1) is None
    True

Cleanup:

    >>> do_action_for(sample1, "recover")
    (...)
    >>> set_retention_rules([])
