##########################################################################
#                                                                        #
#              copyright (c) 2006 +++ sunweavers.net +++                 #
#                                 and contributors                       #
#                                                                        #
#     maintainers: Mike Gabriel, m.gabriel@sunweavers.net                #
#                                                                        #
##########################################################################

""" package installer for ATBiblioTopic """

#from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore.permissions import AddPortalContent
try:
  from Products.LinguaPlone.public import process_types, listTypes
except:
  from Products.Archetypes.public import process_types, listTypes
  
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

PROJECTNAME = 'ATBiblioTopic'
GLOBALS = globals()
skin_names = ('bibliography_topic',)

ADD_CONTENT_PERMISSION = AddPortalContent


registerDirectory('skins', GLOBALS)

import content
import criteria

def initialize(context):

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)