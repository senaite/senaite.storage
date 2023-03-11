## Script (Python) "guard_recover_samples"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from senaite.storage.workflow.samplescontainer.guards import guard_recover_samples
return guard_recover_samples(context)
