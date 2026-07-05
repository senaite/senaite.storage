Changelog
=========

2.7.0 (unreleased)
------------------

- #72 Add printable barcode stickers for storage location objects
- #71 Fix UnicodeDecodeError when running migrate_storage_facility_to_dx
- #68 Require selection of retrieve reason when retrieving samples from storage
- #67 Rename "Recover" transtion to "Retrieve" to align with ISO 17025/15189
- #66 Add visual warning for samples approaching retention expiration
- #65 Add a "Past Retention" filter in samples listing
- #63 Result type-specific controls in retention rules settings
- #64 Add 'Storage Expiry Date' column in samples listing, under 'Stored'
- #62 Add configurable storage retention period
- #61 Added StorageManager and StorageAssistant roles and counterpart groups
- #60 Fix sample search when assigning received samples to storage container
- #59 Fix AttributeError when migrating facilities to DX (2701)
- #58 Fix ValueError: undefined property 'add_permission' on upgrade
- #57 Compatibility with core#2835 (display Storage in navbar)
- #56 Fix UnicodeDecodeError on positions display in storage listing
- #55 Fix Unauthorized error when moving a container across storage
- #54 Fix all storage containers reindexed when other add-ons are upgraded
- #53 Fix AttributeError for containers with more than 25 rows
- #52 Migrate Storage Root Folder to DX
- #51 JS->DX compatibility
- #50 Migrate storage samples container to DX
- #49 Migrate storage container to DX
- #48 Migrate Storage Facility to DX


2.6.0 (2025-04-04)
------------------

- #47 Update permission imports
- #46 Compatibility with core#2584 (SampleType to DX)
- #44 Compatibility with core#2567 (AnalysisCategory to DX)
- #42 Compatibility with core#2471 (Department to DX)
- #39 Add storage settings for auto-store/recover of primary sample
- #38 Remove Script (Python) for guards in favour of guard_handler


2.5.0 (2024-01-11)
------------------

- #37 Migrate Sample/Container Reference Fields to new Widget


2.4.1 (2023-03-11)
------------------

- #36 Remove code headers from Script (Python)


2.4.0 (2023-03-10)
------------------

- Version 2.3.0 -> 2.4.0


2.3.0 (2022-10-03)
------------------

- Version 2.2.0 -> 2.3.0


2.2.0 (2022-06-10)
------------------

- #34 Fix non-lab users can access to storage


2.1.1 (2022-01-08)
------------------

- #32 Fixed catalogs in page templates


2.1.0 (2022-01-05)
------------------

- #30 Compatibility with Senaite catalog migration
- #28 Added upgrade step event subscriber
- #27 Integrate dispatch workflow from senaite.core
- #26 Disallow to modify portal content when stored/booked out samples
- #25 Remove booked out samples from container
- #23 Allow storage container to be booked out
- #22 Allow to move containers
- #21 Allow storage contents to be deactivated
- #20 Added uninstall profile
- #19 Improved storage listing and structuring with positions


2.0.0 (2020-10-19)
------------------

- Added full hierarchy filter in containers listings
- #15 Fixed imports to senaite.app.listing
- Do not display Containers and SampleContainers in navbar by default
- Compatibility with senaite.lims 2.x


1.0.2 (2020-08-11)
------------------

- #14 Refactor folderitem for storage listings to get full object from brain


1.0.1 (2020-03-07)
------------------

- #11 Changed Base Catalog Tool
- #8 Make primary sample to follow partitions on store/recover


1.0.0 (2019-04-01)
------------------

- First version of `senaite.storage`


1.0.0 (2019-10-31)
------------------

- #10 ALLOW SAMPLES TO BE SCANNED WHEN STORING
