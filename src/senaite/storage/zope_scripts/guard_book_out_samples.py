## Script (Python) "guard_book_out_samples"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from senaite.storage.workflow.samplescontainer.guards import guard_book_out_samples
return guard_book_out_samples(context)
