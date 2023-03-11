## Script (Python) "guard_recover_sample"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from senaite.storage.workflow.sample.guards import guard_recover_sample
return guard_recover_sample(context)
