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

from Products.ATContentTypes.atct import ATTopic
from Products.ATContentTypes.criteria import _criterionRegistry
from Products.ATContentTypes.interfaces import IATTopicSortCriterion

try:
  from Products.LinguaPlone.public import registerType
  from Products.LinguaPlone.public import DisplayList
  
except:
  from Products.Archetypes.public import registerType
  from Products.Archetypes.public import DisplayList
 
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATBiblioTopic.config import PROJECTNAME
from Products.ATResearchProject.config import BIBLIOTOPIC_CRITERIAFIELDS
from Products.ATResearchProject.config import BIBLIOTOPIC_SORTFIELDS

"""
bibliotopic.py: renders a smart bibliography list based on ATTopic
"""

class BibliographyTopic(ATTopic):
    """Content type for dynamic listings of research projects / subprojects.
    """

    __implements__  = (ATTopic.__implements__,
		      )

    schema 	    = ATResearchProjectListSchema

    content_icon    = 'research_project_list_icon.gif'
    meta_type       = 'ATResearchProjectList'
    portal_type     = 'ResearchProjectList'
    archetype_name  = 'Research Project List'

    allowed_content_types = ('ResearchProjectList',)
    default_view    = 'research_project_list_view'
    immediate_view  = 'research_project_list_view'
    assocMimetypes  = ('application/xhtml+xml','message/rfc822','text/*')
    
    typeDescription = ("Use this folderish content type to specify a research project search criterion. According to the specified search criterion, a research project list always renders a current list of research projects and subprojects on your site.")
    typeDescMsgId   = 'description_edit_researchprojectlist'
    
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
        'action'      : 'string:${folder_url}/rplist_criterion_edit_form',
        'permissions' : (atct_permissions.ChangeTopics,)
        },
	{
	 'id'          : 'subtopics',
	 'name'        : 'Subfolders',
	 'action'      : 'string:${folder_url}/atct_topic_subtopics',
	 'permissions' : (atct_permissions.ChangeTopics,)
        },
	{
	'id': 'external_edit',
	'name': 'External Edit',
	'action': 'string:${object_url}/external_edit',
	'condition': 'object/externalEditorEnabled',
	'permissions': (permissions.ModifyPortalContent,),
	'visible': 0,
        },
	{
        'id': 'local_roles',
        'name': 'Sharing',
        'action': 'string:${object_url}/folder_localrole_form',
	'permissions': (permissions.ManageProperties,),
        },
    )

    security = ClassSecurityInfo()

    # ResearchProjectList custom properties
    portal_type_to_query = None

    security.declareProtected(atct_permissions.ChangeTopics, 'getSortCriterion')
    def getSortCriterion(self):
	"""return criterion object"""
	for criterion in self.listCriteria():
	    if criterion.Field() in [ crit_field['field'][0] for crit_field in PROJECTLIST_SORTFIELDS if crit_field['portal_type'] == self.getPortalTypeToQuery() ]:
    		if IATTopicSortCriterion.isImplementedBy(criterion):
		    return criterion
	return None
    
    security.declareProtected(atct_permissions.ChangeTopics, 'criteriaByIndexId')
    def criteriaByIndexId(self, indexId):
        # do not change the order of PROJECTLIST_SORTFIELDS + PROJECTLIST_CRITERIAFIELDS
	# otherwise, sorting will be disabled!!!
	for record in PROJECTLIST_SORTFIELDS + PROJECTLIST_CRITERIAFIELDS:
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
   	    remove_sortcrits_from_query = [ crit_field['field'][0] for crit_field in PROJECTLIST_SORTFIELDS if (crit_field['portal_type'] != self.portal_type_to_query) ]
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
        
        # we have to reinstitute some standard index fields, if we have acquired criterias from "superior"
        try:	    
            if query['sort_on'] == 'sortable_title' and (portal_type_to_query == 'ResearchProject'):
                query['sort_on'] == 'titleResearchProject'
            if query['sort_on'] == 'sortable_title' and (portal_type_to_query == 'ResearchSubroject'):
                query['sort_on'] == 'titleResearchSubproject'
        except:
            pass
	    
        if query.has_key('SearchableText') and (portal_type_to_query == 'ResearchProject'):
            query['searchableResearchProjectText'] == query['SearchableText']
	    del query['SearchableText']
        if query.has_key('SearchableText') and (portal_type_to_query == 'ResearchSubroject'):
            query['searchableResearchSubprojectText'] == query['SearchableText']
	    del query['SearchableText']

        if query.has_key('path') and (portal_type_to_query == 'ResearchProject'):
            query['pathResearchProject'] == query['path']
    	    del query['path']
        if query.has_key('path') and (portal_type_to_query == 'ResearchSubroject'):
            query['pathResearchSubproject'] == query['path']
	    del query['path']
    
        #print "0. %s: %s" % (self.portal_type_to_query, query)
        
        if query:
	
	    if not self.portal_type_to_query:

		#
		# for the case portal_type_to_query is not set, this should not occur!!!
		#

		# query ResearchProjects only
		query['portal_type'] = ['ResearchProject',]
		# but if a ResearchSubproject field is queried, switch over to RsearchProjects 
		# and ResearchSubprojects (works around field acquisition from ResearchProject-only
		# fields in ResearchSubprojects).
		for field in [ crit_field['field'] for crit_field in PROJECTLIST_CRITERIAFIELDS if (crit_field['portal_type'] == 'ResearchSubproject') ]:
		    if field[0] in query.keys():
	    		query['portal_type'].append('ResearchSubproject')
	    		break
		
	    else:
		# portal_type_to_query has been set by self.setPortalTypeToQueryFor(<portal_type>).
	        # from now on we will go through a distinguished algorithm that separates Research Projects
		# from Subproject. This makes it possible to specify logic-OR queries and PortalType specific sort order!!!
		
		remove_crits_from_query = [ crit_field['field'][0] for crit_field in PROJECTLIST_CRITERIAFIELDS if (crit_field['portal_type'] != self.portal_type_to_query) ]
		# remove criteria from the query dict that do not belong to the content type queried for
		for query_item in query.keys():
		    if query_item in remove_crits_from_query:
			del query[query_item]
			
                #print "1. %s: %s" % (self.portal_type_to_query, query)
        
                allowed_crits_in_query = [ crit_field['field'][0] for crit_field in PROJECTLIST_CRITERIAFIELDS if crit_field['portal_type'] == self.portal_type_to_query ]
		# check if one of the remaining criteria belongs to the content type queried for
		query_ok = True
                for key in query.keys():
		    if key not in allowed_crits_in_query + ['sort_on', 'sort_order', 'portal_type', 'review_state' ]:
			break
		
                #print "2. %s: %s (query_ok = %s)" % (self.portal_type_to_query, query, query_ok)

		# in any case, we have to override the sort_on query entry!!!
		for criteria in self.listCriteria():
		    if (criteria.Field() in [ crit_field['field'][0] for crit_field in PROJECTLIST_SORTFIELDS if crit_field['portal_type'] == self.getPortalTypeToQuery() ]) and (criteria.meta_type == 'ATSortCriterion'):
                        query['sort_on'] = criteria.Field()
			if criteria.getReversed():
			  query['sort_order'] = 'reverse'
                        else:
                          if query.has_key('sort_order'):
                              del query['sort_order']  

                if query.has_key('sort_on') and query['sort_on'] in ['titleResearchProject', 'titleResearchSubproject',]:
 		    query['sort_on'] = 'sortable_title'

                #print "3. %s: %s" % (self.portal_type_to_query, query)

		# if no criteria remains that belongs to the content type queried for,
		# we need this hack to return an empty brain form the catalog tool
		if not query_ok or not query:
		    query['portal_type'] = ()
		else:
		    query['portal_type'] = tuple([self.portal_type_to_query])
		
		if 'searchableResearchProjectText' in query.keys():
		    query['SearchableText'] = query['searchableResearchProjectText']
		    del query['searchableResearchProjectText']
		if 'searchableResearchSubprojectText' in query.keys():
		    query['SearchableText'] = query['searchableResearchSubprojectText']
		    del query['searchableResearchSubprojectText']

		if 'pathResearchProject' in query.keys():
		    query['path'] = query['pathResearchProject']
		    del query['pathResearchProject']
		if 'pathResearchSubproject' in query.keys():
		    query['path'] = query['pathResearchSubproject']
		    del query['pathResearchSubproject']

                #print "4. %s: %s" % (self.portal_type_to_query, query)


       	    # show only items that are allowed to be shown and not in any hidden review state
	    navtool = getToolByName(self, 'portal_properties').navtree_properties
	    if navtool.getProperty('enable_wf_state_filtering', False):
        	if mtool.isAnonymousUser() or self.getResearchProjectListFilterWorkflowStates():

            	    query['review_state'] = navtool.wf_states_to_show

        #print query

        return query or None

    security.declareProtected(permissions.View, 'setPortalTypeToQuery')
    def setPortalTypeToQuery(self, ptype):
	"""A switch deciding for which portal_type the catalog is queried.
	   If ptype is an empty string, a combined query is performed: 
	   If Research-Project-only-attributes are in the criteria list, 
	   only Research Projects are queried for, if a Subproject-attribute 
	   is in the criteria list, the catalog is queried Research Projects 
	   and Subprojects."""
	if ptype in ['ResearchProject', 'ResearchSubproject']:
	    self.portal_type_to_query = ptype
	    return True
	else:
	    self.portal_type_to_query = None

	return False
	
    security.declareProtected(permissions.View, 'getPortalTypeToQuery')
    def getPortalTypeToQuery(self):
	"""Return the portal_type that would be considered in buildQuery requests."""
	return self.portal_type_to_query
	
    security.declareProtected(permissions.View, 'allowedCriteriaForField')
    def allowedCriteriaForField(self, field, display_list=False):
        """ Return all valid criteria for a given field.  Optionally include
            descriptions in list in format [(desc1, val1) , (desc2, val2)] for
            javascript selector."""
        allowed = [ crit_field['ctypes'] for crit_field in PROJECTLIST_CRITERIAFIELDS if crit_field['field'][0] == field ][0]
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
	addable_fields = [ crit_field['field'] for crit_field in PROJECTLIST_CRITERIAFIELDS if crit_field['field'][0] not in current ]
        return addable_fields

    security.declareProtected(permissions.View, 'listMetaDataFields')
    def listMetaDataFields(self, exclude=True):
        """Return a list of fields for the sortable table.
        """
	atrp_tool = getToolByName(self, 'portal_researchproject')
	indexes = [ crit_field['field'][0] for crit_field in PROJECTLIST_CRITERIAFIELDS + PROJECTLIST_SORTFIELDS if crit_field['field'][0].startswith('research') ]
        table_fields = [ atrp_tool.getRPListCriteriaIndex(index) for index in  indexes ]
        return DisplayList([('Title', 'Title')] + [ (field.index, field.friendlyName or field.index) for field in table_fields ])

    security.declareProtected(atct_permissions.ChangeTopics, 'listSortFields')
    def listSortFields(self):
        """Return a list of available sort fields.
        """
	return [ sort_field['field'] for sort_field in PROJECTLIST_SORTFIELDS if self.validateAddCriterion(sort_field['field'][0], 'ATSortCriterion') and sort_field['portal_type'] == self.getPortalTypeToQuery() ]

registerType(ResearchProjectList,PROJECTNAME)
