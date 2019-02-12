.. image:: https://raw.githubusercontent.com/senaite/senaite.storage/master/static/logo.png
   :alt: senaite.storage
   :width: 500px
   :align: center

— **SENAITE.STORAGE**: *Sample storage add-on for SENAITE*

.. image:: https://img.shields.io/pypi/v/senaite.storage.svg?style=flat-square
   :target: https://pypi.python.org/pypi/senaite.storage

.. image:: https://img.shields.io/github/issues-pr/senaite/senaite.storage.svg?style=flat-square
   :target: https://github.com/senaite/senaite.storage/pulls

.. image:: https://img.shields.io/github/issues/senaite/senaite.storage.svg?style=flat-square
   :target: https://github.com/senaite/senaite.storage/issues

.. image:: https://img.shields.io/badge/README-GitHub-blue.svg?style=flat-square
   :target: https://github.com/senaite/senaite.storage#readme


Introduction
============

SENAITE STORAGE adds **Sample storage** capabilities to SENAITE.


Installation
============

Please follow the installations instructions for `Plone 4`_ and
`senaite.lims`_.

To install SENAITE STORAGE, you have to add `senaite.storage` into the `eggs`
list inside the `[buildout]` section of your `buildout.cfg`::

   [buildout]
   parts =
       instance
   extends =
       http://dist.plone.org/release/4.3.18/versions.cfg
   find-links =
       http://dist.plone.org/release/4.3.18
       http://dist.plone.org/thirdparty
   eggs =
       Plone
       Pillow
       senaite.lims
       senaite.storage
   zcml =
   eggs-directory = ${buildout:directory}/eggs

   [instance]
   recipe = plone.recipe.zope2instance
   user = admin:admin
   http-address = 0.0.0.0:8080
   eggs =
       ${buildout:eggs}
   zcml =
       ${buildout:zcml}

   [versions]
   setuptools =
   zc.buildout =


**Note**

The above example works for the buildout created by the unified
installer. If you however have a custom buildout you might need to add
the egg to the `eggs` list in the `[instance]` section rather than
adding it in the `[buildout]` section.

Also see this section of the Plone documentation for further details:
https://docs.plone.org/4/en/manage/installing/installing_addons.html

**Important**

For the changes to take effect you need to re-run buildout from your
console::

   bin/buildout


Installation Requirements
-------------------------

The following versions are required for SENAITE STORAGE:

-  Plone 4.3.18
-  senaite.core >= 1.2.9
-  senaite.lims >= 1.2.0


Screenshots
-----------

.. image:: https://raw.githubusercontent.com/senaite/senaite.storage/master/static/storage_facilities.png
   :alt: Storage facilities
   :width: 760px
   :align: center

.. image:: https://raw.githubusercontent.com/senaite/senaite.storage/master/static/container_listing.png
   :alt: Containers and sample containers
   :width: 760px
   :align: center

.. image:: https://raw.githubusercontent.com/senaite/senaite.storage/master/static/samples_listing.png
   :alt: Store transition in samples listings
   :width: 760px
   :align: center

.. image:: https://raw.githubusercontent.com/senaite/senaite.storage/master/static/samples_assignment_to_container.png
   :alt: Assignment of samples in a container
   :width: 760px
   :align: center

.. image:: https://raw.githubusercontent.com/senaite/senaite.storage/master/static/samples_assignment_to_multiple.png
   :alt: Assignment of samples to multiple containers
   :width: 760px
   :align: center

.. _Plone 4: https://docs.plone.org/4/en/manage/installing/index.html
.. _senaite.lims: https://github.com/senaite/senaite.lims#installation
