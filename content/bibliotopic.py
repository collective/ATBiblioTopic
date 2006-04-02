#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Acquisition import aq_parent, aq_inner

from Products.CMFCore import permissions
from Products.ATContentTypes import permission as atct_permissions

from Products.CMFCore.utils import getToolByName

from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized

from Products.ATContentTypes.atct import ATTopic, ATTopicSchema
from Products.ATContentTypes.criteria import _criterionRegistry
from Products.ATContentTypes.interfaces import IATTopicSortCriterion

try:
  from Products.LinguaPlone.public import Schema, MetadataSchema
  from Products.LinguaPlone.public import registerType
  from Products.LinguaPlone.public import DisplayList
  from Products.LinguaPlone.public import StringField, ReferenceField, BooleanField
  from Products.LinguaPlone.public import SelectionWidget, ReferenceWidget, BooleanWidget
  
except:
  from Products.Archetypes.public import Schema, MetadataSchema
  from Products.Archetypes.public import registerType
  from Products.Archetypes.public import DisplayList
  from Products.Archetypes.public import StringField, ReferenceField, BooleanField
  from Products.Archetypes.public import SelectionWidget, ReferenceWidget, BooleanWidget
 
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.Archetypes.Marshall import PrimaryFieldMarshaller

from Products.ATBiblioTopic.config import PROJECTNAME
from Products.ATBiblioTopic.config import LISTING_VALUES
from Products.ATBiblioTopic.config import ATBIBLIOTOPIC_BIBFOLDER_REF
from Products.ATBiblioTopic.config import BIBLIOTOPIC_CRITERIAFIELDS
from Products.ATBiblioTopic.config import BIBLIOTOPIC_SORTFIELDS
from Products.ATBiblioTopic.config import BIBLIOTOPIC_INDEXES

# possible types of bibliographic references from module 'CMFBibliographyAT'
from Products.CMFBibliographyAT.config import REFERENCE_TYPES as search_types, \
     FOLDER_TYPES as BIB_FOLDER_TYPES, \
     ADD_CONTENT_PERMISSION as BIBFOLDER_ADD_CONTENT_PERMISSION
          
"""
bibliotopic.py: renders a smart bibliography list based on ATTopic
"""


def _getBiblioTopicCriteriaIndex(index_name):

    if BIBLIOTOPIC_INDEXES.has_key(index_name):
        return BIBLIOTOPIC_INDEXES[index_name]
    else:
        raise AttributeError ('Index ' + str(index_name) + ' not found')
                                                    
relatedItemsField = ReferenceField('relatedItems',
        relationship = 'relatesTo',
        multiValued = True,
        isMetadata = True,
        languageIndependent = False,
        index = 'KeywordIndex',
        write_permission = permissions.ModifyPortalContent,
        widget = ReferenceBrowserWidget(
                        allow_search = True,
                        allow_browse = True,
                        show_indexes = False,
                        force_close_on_insert = True,
                        label = "Related Item(s)",
                        label_msgid = "label_related_items",
                        description = "Reference other items on your site here.",
                        description_msgid = "help_related_items",
                        i18n_domain = "plone",
                        visible = {'edit' : 'visible', 'view' : 'invisible' },
        ),
)

BiblioTopicSchema = ATTopicSchema.copy() + Schema(
    (
        StringField('ListingLayout',
            multiValued=0,
            default = "bulletted",
            vocabulary=LISTING_VALUES,
            enforce_vocabulary=1,
            widget=SelectionWidget(label="Listing Layout",
                        label_msgid="label_bibliotopic_listing_layout",
                        description_msgid="help_bibliotopic_listing_layout",
                        description="Listing Format.",
                        i18n_domain="atbibliotopic",
                        format="pulldown",
                        visible={'edit':'visible','view':'invisible'},
            ),
        ),
        StringField('PresentationStyle',
            multiValued=0,
            default = 'stl_minimal',
            vocabulary="vocabCustomStyle",
            enforce_vocabulary=1,
            widget=SelectionWidget(label="Bibliographical Style",
                        label_msgid="label_bibliotopic_presentation",
                        description_msgid="help_bibliotopic_presentation",
                        description="Bibliographical Style used for display.",
                        i18n_domain="atbibliotopic",
                        format="select",
                        visible={'edit':'visible','view':'invisible'},
            ),
        ),
        BooleanField('linkToOriginalRef',
            widget=BooleanWidget(label="Link to Original Reference",
                        label_msgid="label_bibliotopic_linktooriginalref",
                        description_msgid="help_bibliotopic_linktooriginalref",
                        description="Should the bibliographical reference title be a link to the original bibliographical reference?",
                        i18n_domain="atbibliotopic",
                        visible={'edit':'visible','view':'invisible'},
            ),
        ),
        ReferenceField('associatedBibFolder',
            multiValued=0,
            relationship=ATBIBLIOTOPIC_BIBFOLDER_REF,
            allowed_types=BIB_FOLDER_TYPES,
            widget=ReferenceWidget(label="Associated ",
                        label_msgid="label_associated_bibfolder",
                        description_msgid="help_associated_bibfolder",
                        description="Associates a specific BibliographyFolder with this list for the purpose of uploads only.",
                        i18n_domain="atbibliotopic",
            ),      
        ),
        relatedItemsField,
    ), marshall=PrimaryFieldMarshaller,
) + MetadataSchema(
    (
        BooleanField('excludeFromNav',
            required = False,
            languageIndependent = True,
            schemata = 'metadata', # moved to 'default' for folders
            widget = BooleanWidget(
                        description="If selected, this item will not appear in the navigation tree",
                        description_msgid = "help_exclude_from_nav",
                        label = "Exclude from navigation",
                        label_msgid = "label_exclude_from_nav",
                        i18n_domain = "plone",
                        visible={'view' : 'hidden', 'edit' : 'visible'},
            ),
        ),
    )
)
BiblioTopicSchema['limitNumber'].languageIndependent = True
BiblioTopicSchema['itemCount'].languageIndependent = True
BiblioTopicSchema['customView'].languageIndependent = True
BiblioTopicSchema['customViewFields'].languageIndependent = True
BiblioTopicSchema.moveField('acquireCriteria', after='description')
BiblioTopicSchema.moveField('ListingLayout', after='acquireCriteria')
BiblioTopicSchema.moveField('PresentationStyle', after='ListingLayout')
BiblioTopicSchema.moveField('linkToOriginalRef', after='PresentationStyle')
BiblioTopicSchema.moveField('associatedBibFolder', after='linkToOriginalRef')
BiblioTopicSchema.moveField('relatedItems', after='customViewFields')

class BibliographyTopic(ATTopic):
    """Content type for dynamic listings of bibliographical references.
    """

    __implements__  = (ATTopic.__implements__,
		      )

    schema 	    = BiblioTopicSchema

    content_icon    = 'bibliotopic_icon.gif'
    meta_type       = 'ATBiblioTopic'
    portal_type     = 'BiblioTopic'
    archetype_name  = 'Smart Bibliography List'
    _at_rename_after_create = True

    allowed_content_types = ('BiblioTopic',)
    default_view    = 'bibliotopic_view'
    immediate_view  = 'bibliotopic_view'
    assocMimetypes  = ('application/xhtml+xml','message/rfc822','text/*')
    
    typeDescription = ("Use this folderish content type to specify a bibliography search criterion. According to the specified search criteria, a smart bibliography list always renders a current list of your site's bibliographical reference items.")
    typeDescMsgId   = 'description_edit_bibliotopic'
    
    actions = (
	{
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${folder_url}/',
        'permissions' : (permissions.View,)
        },
	{
        'id'          : 'edit',
	'name'        : 'Edit',
	'action'      : 'string:${object_url}/edit',
	'permissions' : (atct_permissions.ChangeTopics,)
        },
	{
        'id'          : 'criteria',
        'name'        : 'Criteria',
        'action'      : 'string:${folder_url}/bibliotopic_criterion_edit_form',
        'permissions' : (atct_permissions.ChangeTopics,)
        },
	{
	 'id'          : 'subtopics',
	 'name'        : 'Subfolders',
	 'action'      : 'string:${folder_url}/atct_topic_subtopics',
	 'permissions' : (atct_permissions.ChangeTopics,)
        },
	{
        'id': 'local_roles',
        'name': 'Sharing',
        'action': 'string:${object_url}/folder_localrole_form',
	'permissions': (permissions.ManageProperties,),
        },
    )

    security = ClassSecurityInfo()

    #security.declareProtected(atct_permissions.ChangeTopics, 'getSortCriterion')
    #def getSortCriterion(self):
    #   """return criterion object"""
    #	for criterion in self.listCriteria():
    #	    if criterion.Field() in [ crit_field['field'][0] for crit_field in BIBLIOTOPIC_SORTFIELDS if crit_field['portal_type'] == self.getPortalTypeToQuery() ]:
    #		if IATTopicSortCriterion.isImplementedBy(criterion):
    #		    return criterion
    #	return None
    
    security.declareProtected(atct_permissions.ChangeTopics, 'criteriaByIndexId')
    def criteriaByIndexId(self, indexId):
        # do not change the order of BIBLIOTOPIC_SORTFIELDS + BIBLIOTOPIC_CRITERIAFIELDS
	# otherwise, sorting will be disabled!!!
	for record in BIBLIOTOPIC_SORTFIELDS + BIBLIOTOPIC_CRITERIAFIELDS:
	    if indexId == record['field'][0]:
		return record['ctypes']
	return ()

    security.declareProtected(permissions.View, 'buildQuery')
    def buildQuery(self, **kw):
        """Build Query
        """

	query = {}
	criteria = self.listCriteria()
        acquire = self.getAcquireCriteria()
        mtool = getToolByName(self, 'portal_membership')

        if not acquire and not criteria:
	  print 'query is NONE'
          return None 

        #print "init %s: %s" % (self.portal_type_to_query, query)

        if acquire:
            try: 
                parent = aq_parent(aq_inner(self))
                parent.setPortalTypeToQuery(self.portal_type_to_query)
                query.update(parent.buildQuery(**kw))
            except (AttributeError, Unauthorized):
                pass
                    
        for criterion in criteria:
        
            remove_sort_order = False
  	    remove_sortcrits_from_query = [ crit_field['field'][0] for crit_field in BIBLIOTOPIC_SORTFIELDS ]
            for key, value in criterion.getCriteriaItems():
                if (key == 'sort_on') and (value in remove_sortcrits_from_query):
                    remove_sort_order = True
                    pass    
                else:      
                    query[key] = value
                    
            if remove_sort_order:
                try:
                    del query['sort_order']        
                except: 
                    pass
        
        print query

        return query or None

    security.declareProtected(permissions.View, 'allowedCriteriaForField')
    def allowedCriteriaForField(self, field, display_list=False):
        """ Return all valid criteria for a given field.  Optionally include
            descriptions in list in format [(desc1, val1) , (desc2, val2)] for
            javascript selector."""
        allowed = [ crit_field['ctypes'] for crit_field in BIBLIOTOPIC_CRITERIAFIELDS if crit_field['field'][0] == field ][0]
	if display_list:
	    flat = []
	    for a in allowed:
	        desc = _criterionRegistry[a].shortDesc
	        flat.append((a,desc))
	    allowed = DisplayList(flat)
	return allowed
																						    
    security.declareProtected(atct_permissions.ChangeTopics, 'listAvailableFields')
    def listAvailableFields(self):
        """Return a list of available fields for new criteria.
        """
        # first we filter out fields that are already in the criteria list
        current = [ crit.Field() for crit in self.listCriteria() if crit.meta_type != 'ATSortCriterion' ]
	addable_fields = [ crit_field['field'] for crit_field in BIBLIOTOPIC_CRITERIAFIELDS if crit_field['field'][0] not in current ]
        return addable_fields

    security.declareProtected(permissions.View, 'listMetaDataFields')
    def listMetaDataFields(self, exclude=True):
        """Return a list of fields for the sortable table.
        """
        indexes = [ crit_field['field'][0] for crit_field in BIBLIOTOPIC_CRITERIAFIELDS + BIBLIOTOPIC_SORTFIELDS if crit_field['custom_view'] ]
        table_fields = [ _getBiblioTopicCriteriaIndex(index) for index in  indexes ]
        return [ ('Title', 'Title') ] + [ (field.index, field.friendlyName or field.index) for field in table_fields ]

    security.declareProtected(atct_permissions.ChangeTopics, 'listSortFields')
    def listSortFields(self):
        """Return a list of available sort fields.
        """
	return [ sort_field['field'] for sort_field in BIBLIOTOPIC_SORTFIELDS if self.validateAddCriterion(sort_field['field'][0], 'ATSortCriterion') ]

registerType(BibliographyTopic, PROJECTNAME)
