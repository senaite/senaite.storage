## Script (Python) "guard_add_samples"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from senaite.storage.workflow.samplescontainer.guards import guard_add_samples
return guard_add_samples(context)
