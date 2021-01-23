## Script (Python) "guard_move_container"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from senaite.storage.workflow.storage.guards import guard_move_container
return guard_move_container(context)
