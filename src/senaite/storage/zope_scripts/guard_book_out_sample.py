## Script (Python) "guard_book_out_sample"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from senaite.storage.workflow.sample.guards import guard_book_out_sample
return guard_book_out_sample(context)
