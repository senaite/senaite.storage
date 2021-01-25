## Script (Python) "guard_store_sample"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from senaite.storage.workflow.sample.guards import guard_store_sample
return guard_store_sample(context)
