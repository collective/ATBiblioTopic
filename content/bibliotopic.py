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

import types

from Acquisition import aq_parent, aq_inner
import Missing

from Products.CMFCore import permissions
from Products.ATContentTypes import permission as atct_permissions

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import registerIndexableAttribute    

from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized

from Products.ATContentTypes.atct import ATTopic, ATTopicSchema
from Products.ATContentTypes.criteria import _criterionRegistry
from Products.ATContentTypes.interfaces import IATTopicSortCriterion

try:
  from Products.LinguaPlone.public import Schema, MetadataSchema
  from Products.LinguaPlone.public import registerType, listTypes
  from Products.LinguaPlone.public import DisplayList
  from Products.LinguaPlone.public import StringField, ReferenceField, BooleanField, TextField
  from Products.LinguaPlone.public import SelectionWidget, ReferenceWidget, BooleanWidget, RichWidget
  
except:
  from Products.Archetypes.public import Schema, MetadataSchema
  from Products.Archetypes.public import registerType, listTypes
  from Products.Archetypes.public import DisplayList
  from Products.Archetypes.public import StringField, ReferenceField, BooleanField, TextField
  from Products.Archetypes.public import SelectionWidget, ReferenceWidget, BooleanWidget, RichWidget
 
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.Archetypes.Marshall import PrimaryFieldMarshaller

from Products.ATBiblioTopic.config import PROJECTNAME
from Products.ATBiblioTopic.config import LISTING_VALUES, STRUCTURAL_VALUES
from Products.ATBiblioTopic.config import ATBIBLIOTOPIC_BIBFOLDER_REF
from Products.ATBiblioTopic.config import BIBLIOTOPIC_CRITERIAFIELDS
from Products.ATBiblioTopic.config import BIBLIOTOPIC_SORTFIELDS
from Products.ATBiblioTopic.config import BIBLIOTOPIC_INDEXES

# possible types of bibliographic references from module 'CMFBibliographyAT'
from Products.CMFBibliographyAT.config import \
     FOLDER_TYPES as BIB_FOLDER_TYPES, \
     ADD_CONTENT_PERMISSION as BIBFOLDER_ADD_CONTENT_PERMISSION, \
     PROJECTNAME as BIBLIOGRAPHY_PROJECTNAME
     
from Products.CMFBibliographyAT.content.folder import BibliographyFolder, LargeBibliographyFolder
          
"""
bibliotopic.py: renders a smart bibliography list based on ATTopic
"""


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
                        force_close_on_insert = False,
                        label = "Related Item(s)",
                        label_msgid = "label_related_items",
                        description = "Reference other items on your site here.",
                        description_msgid = "help_related_items",
                        i18n_domain = "plone",
                        visible = {'edit' : 'visible', 'view' : 'invisible' },
        ),
)

BibliographyTopicSchema = ATTopicSchema.copy() + Schema(
    (
        TextField('biblioTopicHeader',
            searchable = True,
            required=0,
            default_content_type='text/html',
            default_output_type='text/html',
            allowable_content_types=('text/html',),
            widget=RichWidget(
                label='Smart Bibliography List Header',
                label_msgid='label_bibliotopic_header',
                description='Text entered here will be displayed as a header above the actual list of bibliographical references.',
                description_msgid='help_bibliotopic_header',
                i18n_domain = 'atbibliotopic',
                rows=8,
            ),
        ),
        BooleanField('acquireCriteria',
            required=False,
            mode="rw",
            default=True,
            languageIndependent=True,
            widget=BooleanWidget(
		label="Inherit Criteria",
		label_msgid="label_inherit_criteria",
		description="Narrow down the search results from the parent Smart Bibliography List by using the criteria from this Smart Bibliography List.",
                description_msgid="help_inherit_criteria",
                i18n_domain = "atbibliotopic",
                condition = "python:folder.getParentNode().portal_type == 'BibliographyTopic'",
            ),
        ),
        StringField('ListingLayout',
            multiValued=0,
            default = "bulletted",
            vocabulary=LISTING_VALUES,
    	    languageIndependent = True,
            enforce_vocabulary=1,
            widget=SelectionWidget(
                label="Layout of Bibliography Listing (HTML)",
                label_msgid="label_bibliotopic_listinglayout",
                description_msgid="help_bibliotopic_listinglayout",
                description="HTML format used for the list of bibliographical items. If you do not want your bibliography list arranged in HTML lists or tables, choose 'Simple lines list' here.",
                i18n_domain="atbibliotopic",
                format="pulldown",
                visible={'edit':'visible','view':'invisible'},
            ),
        ),
        StringField('StructuralLayout',
            multiValued=0,
            default = 'none',
            vocabulary=STRUCTURAL_VALUES,
    	    languageIndependent = True,
            enforce_vocabulary=1,
            widget=SelectionWidget(
                label="Structural Layout",
                label_msgid="label_bibliotopic_structurallayout",
                description_msgid="help_bibliotopic_structurallayout",
                description="Choose a field that shall be used to structure your smart bibliography list. This feature allows you to sort your list of bibliographical items on two levels. Try this: choose publication year here and use authors as the lists sort criterion in the criteria tab of this list. You will get a list of bibliographical references grouped by publication years. For each publication year, however, the bibliographical items will be sorted by author names.",
                i18n_domain="atbibliotopic",
                format="pulldown",
                visible={'edit':'visible','view':'invisible'},
            ),
        ),
        BooleanField('StructuralLayoutReverseOrder',
            default = False,
    	    languageIndependent = True,
            widget=BooleanWidget(
		label="Reverse Sort Order of Structural Layout",
                label_msgid="label_bibliotopic_structurallayoutreverseorder",
                description_msgid="help_bibliotopic_structurallayoutreversesortorder",
                description="Click here if you want to structure this smart bibliography list in reverse order.",
                i18n_domain="atbibliotopic",
                format="pulldown",
                visible={'edit':'visible','view':'invisible'},
            ),
        ),
        StringField('PresentationStyle',
            multiValued=0,
            default = 'stl_minimal',
            vocabulary="vocabCustomStyle",
    	    languageIndependent = True,
            enforce_vocabulary=1,
            widget=SelectionWidget(
                label="Bibliographical Style",
                label_msgid="label_bibliotopic_presentation",
                description_msgid="help_bibliotopic_presentation",
                description="Bibliographical style used for display. You can either choose one of the hard-coded bibliography styles here or utilize your own bibliography styles from your custom style sets.",
                i18n_domain="atbibliotopic",
                format="select",
                visible={'edit':'visible','view':'invisible'},
            ),
        ),
        BooleanField('linkToOriginalRef',
    	    languageIndependent = True,
            widget=BooleanWidget(
                label="Link to Page of Bibliographical Entry",
                label_msgid="label_bibliotopic_linktooriginalref",
                description_msgid="help_bibliotopic_linktooriginalref",
                description="Should a bibliographical item's title in the list be a link to the page of the bibliographical reference?",
                i18n_domain="atbibliotopic",
                visible={'edit':'visible','view':'invisible'},
            ),
        ),
        BooleanField('linkToOriginalRefOnlyIfOwner',
	    default = False,
    	    languageIndependent = True,
            widget=BooleanWidget(
                label="Only Show Link to Bibliographical Entry Page If Owner",
                label_msgid="label_bibliotopic_linktooriginalrefonlyifowner",
                description="If linking to pages of bibliographical entries is enabled, this switch will narrow the number of linked entries down to those items the authenticated user is owner of.",
                description_msgid="help_bibliotopic_linktooriginalrefonlyifowner",
                i18n_domain="atbibliotopic",
                visible={'edit':'visible','view':'invisible'},
            ),
        ),
        BooleanField('filterReferencesByWorkflowState',
    	    languageIndependent = True,
            widget=BooleanWidget(
                label="Filter References By Workflow State",
                label_msgid="label_bibliotopic_filterreferencesbyworkflowstate",
                description_msgid="help_bibliotopic_filterreferencesbyworkflowstate",
                description="Show bibliographical reference items only if their workflow state allows it.",
                i18n_domain="atbibliotopic",
                visible={'edit':'visible','view':'invisible'},
            ),
        ),
        BooleanField('noWfStateFilterIfUserCanModifyBibrefContent',
            old_field_name = 'noWfStateFilterIfOwnerOfReference',
    	    languageIndependent = True,
            widget=BooleanWidget(
                label="No Workflow State Filter if User can Modify Content",
                label_msgid="label_bibliotopic_nowfstatefilterifusercanmodifybibrefcontent",
                description_msgid="help_bibliotopic_nowfstatefilterifusercanmodifybibrefcontent",
                description="Do explicitly show non-published bibliographical entries if the authenticated user has permission to modify the entry's content.",
                i18n_domain="atbibliotopic",
                visible={'edit':'visible','view':'invisible'},
            ),
        ),
        ReferenceField('associatedBibFolder',
            multiValued=0,
            relationship=ATBIBLIOTOPIC_BIBFOLDER_REF,
            allowed_types=BIB_FOLDER_TYPES,
    	    languageIndependent = True,
            widget=ReferenceWidget(
                label="Associated Bibliography Folder",
                checkbox_bound=0,
                label_msgid="label_associated_bibfolder",
                description_msgid="help_associated_bibfolder",
                description="Associates one of the portal's bibliography folders to this list for the purpose of uploads (bibliography import).",
                i18n_domain="atbibliotopic",
            ),      
        ),
        TextField('biblioTopicFooter',
            searchable = True,
            required=0,
            default_content_type='text/html',
            default_output_type='text/html',
            allowable_content_types=('text/html',),
            widget=RichWidget(
                label='Smart Bibliography List Footer',
                label_msgid='label_bibliotopic_footer',
                description='Text entered here will be displayed as a footer below the actual list of bibliographical references.',
                description_msgid='help_bibliotopic_footer',
                i18n_domain = 'atbibliotopic',
                rows=8,
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
                        label = "Exclude from navigation",
                        label_msgid = "label_exclude_from_nav",
                        description="If selected, this item will not appear in the navigation tree",
                        description_msgid = "help_exclude_from_nav",
                        i18n_domain = "plone",
                        visible={'view' : 'hidden', 'edit' : 'visible'},
            ),
        ),
    )
)
BibliographyTopicSchema['limitNumber'].languageIndependent = True
BibliographyTopicSchema['itemCount'].languageIndependent = True
BibliographyTopicSchema['customView'].languageIndependent = True
BibliographyTopicSchema['customViewFields'].languageIndependent = True
BibliographyTopicSchema.moveField('biblioTopicHeader', after='description')
BibliographyTopicSchema.moveField('acquireCriteria', after='biblioTopicHeader')
BibliographyTopicSchema.moveField('ListingLayout', after='acquireCriteria')
BibliographyTopicSchema.moveField('StructuralLayout', after='ListingLayout')
BibliographyTopicSchema.moveField('StructuralLayoutReverseOrder', after='StructuralLayout')
BibliographyTopicSchema.moveField('PresentationStyle', after='StructuralLayoutReverseOrder')
BibliographyTopicSchema.moveField('linkToOriginalRef', after='PresentationStyle')
BibliographyTopicSchema.moveField('linkToOriginalRefOnlyIfOwner', after='linkToOriginalRef')
BibliographyTopicSchema.moveField('filterReferencesByWorkflowState', after='linkToOriginalRefOnlyIfOwner')
BibliographyTopicSchema.moveField('noWfStateFilterIfUserCanModifyBibrefContent', after='filterReferencesByWorkflowState')
BibliographyTopicSchema.moveField('associatedBibFolder', after='noWfStateFilterIfUserCanModifyBibrefContent')
BibliographyTopicSchema.moveField('relatedItems', after='biblioTopicFooter')
BibliographyTopicSchema.moveField('excludeFromNav', before='allowDiscussion')

class BibliographyTopic(ATTopic):
    """Content type for dynamic listings of bibliographical references.
    """

    __implements__  = (ATTopic.__implements__,
		      )

    schema 	    = BibliographyTopicSchema

    content_icon    = 'bibliotopic_icon.gif'
    meta_type       = 'ATBibliographyTopic'
    portal_type     = 'BibliographyTopic'
    archetype_name  = 'Smart Bibliography List'
    _at_rename_after_create = True

    allowed_content_types = ('BibliographyTopic',)
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
         'id'          : 'exportBib',
         'name'        : 'Export Bibliography',
         'action'      : 'string:${object_url}/bibliotopic_exportForm',
         'permissions' : (permissions.View, ),
         'category'    : 'document_actions',
        },
        {
         'id'           : 'import',
         'name'         : 'Import',
         'action'       : 'string:${object_url}/bibliography_importForm',
         'permissions'  : (BIBFOLDER_ADD_CONTENT_PERMISSION,),
         'condition'    : 'python:object.getAssociatedBibFolder() is not None',
        },
        {
         'id': 'local_roles',
         'name': 'Sharing',
         'action': 'string:${object_url}/folder_localrole_form',
	 'permissions': (permissions.ManageProperties,),
         'condition': 'python: object.portal_membership.checkPermission("ManageProperties", object)',
	},
    )

    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'vocabCustomStyle')
    def vocabCustomStyle(self):
        """ build a DisplayList based on existing styles
        """
        bstool = getToolByName(self, 'portal_bibliostyles') or None
        return DisplayList(bstool.findBibrefStyles())
                                    
    security.declareProtected(atct_permissions.ChangeTopics, 'criteriaByIndexId')
    def criteriaByIndexId(self, indexId):
        # do not change the order of BIBLIOTOPIC_SORTFIELDS + BIBLIOTOPIC_CRITERIAFIELDS
	# otherwise, sorting will be disabled!!!
	for record in BIBLIOTOPIC_SORTFIELDS + BIBLIOTOPIC_CRITERIAFIELDS:
	    if indexId == record['field'][0]:
		return record['ctypes']
	return ()

    security.declareProtected(permissions.View, 'filterWfStateIfNotOwnerOfReference')
    def filterWfStateIfNotOwnerOfReference(self, unfiltered=None):

	if unfiltered is not None and self.getNoWfStateFilterIfUserCanModifyBibrefContent():
	    
	    navtool = getToolByName(self, 'portal_properties').navtree_properties
            mtool = getToolByName(self, 'portal_membership')
            return [ brain for brain in unfiltered if (self.getFilterReferencesByWorkflowState() and (brain.review_state in navtool.wf_states_to_show)) or mtool.checkPermission(permissions.ModifyPortalContent, brain.getObject()) ]

	return unfiltered

    security.declareProtected(permissions.View, 'getStructuralLayoutRefs')
    def getStructuralLayoutRefs(self, search_result, structural_layout='', structural_layout_reverse=False):

	if structural_layout == 'none':
	    return [search_result]
	    
	catalog = getToolByName(self, 'portal_catalog')
	putils = getToolByName(self, 'plone_utils')
	bib_tool = getToolByName(self, 'portal_bibliography')
	types_tool = getToolByName(self, 'portal_types')
        at_tool = getToolByName(self, 'archetype_tool')
	catalogIndexes = catalog.indexes()
	
	structure_by = []
    	
	data_objects = []
	for item in search_result:
	    path = item.getPath()
	    item_url = item.getURL()
	    brain_data = {
		'path' : path,
		'absolute_url': item_url,
	        'Title': putils.pretty_title_or_id(item),
		'icon': item.getIcon,
                'obj': item.getObject(),
	    }
	    for index in catalogIndexes:
		if hasattr(item, index) and (eval('item.%s' % index) != Missing.Value):
		    brain_data[index] = eval('item.%s' % index)
	    
            data_objects.append(brain_data)
            structure_by_item = None
	    if structural_layout in brain_data.keys():
                structure_by_item = brain_data[structural_layout]
        
            elif callable(getattr(brain_data['obj'], structural_layout, None)):
                structure_by_method = getattr(brain_data['obj'], structural_layout, None)
                try:
                    structure_by_item = structure_by_method()
                except:
                    pass    
                
            if type(structure_by_item) in (types.TupleType, types.ListType):
	        for item in structure_by_item:
                    if item not in structure_by:
                        structure_by.append(item)
            elif structure_by_item:
	        structure_by.append(structure_by_item)
                    
        structural_heads = []
        structural_refs = { 'atbibliotopic_structural_heads_mapping': {}, }
        resolve_heads2atobjects = False
        for struct_head in structure_by:

            if struct_head not in structural_refs.keys():
                structural_heads.append(struct_head)
                structural_refs[struct_head] = []

                ref_obj = at_tool.lookupObject(struct_head)
                if ref_obj and ref_obj.Title() not in structural_refs.keys():
                    structural_refs['atbibliotopic_structural_heads_mapping'][struct_head] = ref_obj.Title()
                    
                else:
                    structural_refs['atbibliotopic_structural_heads_mapping'][struct_head] = self.translate(domain='plone', msgid=struct_head, default=struct_head)
                
        # sort structural layout by mapped structural heads (either object title or i18n translation (if any))...
        mapped_struct_heads = zip(structural_refs['atbibliotopic_structural_heads_mapping'].values(), structural_refs['atbibliotopic_structural_heads_mapping'].keys())
        
        mapped_struct_heads.sort()
	if structural_layout_reverse:
	    mapped_struct_heads.reverse()
            
        structural_refs['atbibliotopic_structural_layout'] = []
        for struct_head in mapped_struct_heads:
            structural_refs['atbibliotopic_structural_layout'].append(struct_head[1])
            
        for item in search_result:
		    
	    for struct_head in structural_heads:
            
                if item.has_key(structural_layout) and (struct_head in item[structural_layout]):
		    structural_refs[struct_head].append(item)
                
                elif callable(getattr(brain_data['obj'], structural_layout, None)):
                    structure_by_method = getattr(item.getObject(), structural_layout, None)
                    if struct_head in structure_by_method():
		        structural_refs[struct_head].append(item)
                
                
                
	return structural_refs

    security.declareProtected(permissions.View, 'buildQuery')
    def buildQuery(self, **kw):
        """Build Query
        """

	query = {}

	criteria = self.listCriteria()
        acquire = self.getAcquireCriteria()
        mtool = getToolByName(self, 'portal_membership')
	bib_tool = getToolByName(self, 'portal_bibliography')
	
        if not acquire and not criteria:
          return None 

        #print "init %s: %s" % (self.portal_type_to_query, query)

        if acquire:
            try: 
                parent = aq_parent(aq_inner(self))
                query.update(parent.buildQuery(**kw))
            except (AttributeError, Unauthorized):
                pass
                    
                
        for criterion in criteria:        

            for key, value in criterion.getCriteriaItems():
            
                query[key] = value

	if query and not query.has_key('portal_type'):
    	    query['portal_type'] = tuple(bib_tool.getReferenceTypes())
	
        if self.getFilterReferencesByWorkflowState():
            navtool = getToolByName(self, 'portal_properties').navtree_properties
            mtool = getToolByName(self, 'portal_membership')
            if query and navtool.getProperty('enable_wf_state_filtering', False):
                if mtool.isAnonymousUser() or not self.getNoWfStateFilterIfUserCanModifyBibrefContent():
            	    query['review_state'] = navtool.wf_states_to_show
		else:
		    pass

        return query or None

    security.declareProtected(permissions.View, 'getBiblioTopicCriteriaIndex')
    def getBiblioTopicCriteriaIndex(self, index_name):

        if BIBLIOTOPIC_INDEXES.has_key(index_name):
            index = BIBLIOTOPIC_INDEXES[index_name]
            return BIBLIOTOPIC_INDEXES[index_name]
        else:
            raise AttributeError ('Index ' + str(index_name) + ' not found')
                                                    
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
    def listMetaDataFields(self):
        """Return a list of fields for the sortable table.
        """
        indexes = [ crit_field['field'][0] for crit_field in BIBLIOTOPIC_CRITERIAFIELDS + BIBLIOTOPIC_SORTFIELDS if crit_field.has_key('custom_view') and crit_field['custom_view'] ]
        table_fields = [ self.getBiblioTopicCriteriaIndex(index) for index in indexes ]
        return [ ('Title', 'Title') ] + [ (field.index, field.friendlyName or field.index) for field in table_fields ]

    security.declareProtected(atct_permissions.ChangeTopics, 'listSortFields')
    def listSortFields(self):
        """Return a list of available sort fields.
        """
	return [ sort_field['field'] for sort_field in BIBLIOTOPIC_SORTFIELDS if self.validateAddCriterion(sort_field['field'][0], 'ATSortCriterion') ]

    security.declareProtected(permissions.View, 'listBibReferenceTypes')
    def listBibReferenceTypes(self):
        """Return a DisplayList containing all available bibref items
        """
	bib_tool = getToolByName(self, 'portal_bibliography')
        return DisplayList(tuple([(type['klass'].portal_type, type['klass'].archetype_name) for type in listTypes(BIBLIOGRAPHY_PROJECTNAME) if type['klass'].portal_type in bib_tool.getReferenceTypes() ]))

    security.declareProtected(permissions.View, 'isAllowedToAddBibReferences')
    def isAllowedToAddBibReferences(self):
        """checks if the current user is allowed to add content to the associated Bibfolder
        """
        mtool = getToolByName(self, 'portal_membership')
        return self.getAssociatedBibFolder() and mtool.checkPermission('ModifyPortalContent', self.getAssociatedBibFolder()) and True or False

    security.declareProtected(permissions.View, 'getAssociatedBibFolderUrl')
    def getAssociatedBibFolderUrl(self):
        """returns the URL of the associated bibfolder
        """
        return self.getAssociatedBibFolder() and self.getAssociatedBibFolder().absolute_url() or False

    security.declareProtected(BIBFOLDER_ADD_CONTENT_PERMISSION, 'processSingleImport')
    def processSingleImport(self, entry, infer_references=True, **kwargs):
        """
        """
        bf = self.getAssociatedBibFolder()
        # No need to put in a security check on the 'real' context (i.e. bf)
        # here because bf.processSingleImport(...) calls self.invokeFactory(...)
        # which has security built-in.

        result =  bf.processSingleImport(entry, infer_references=infer_references, **kwargs)
        if len(result) == 2:
            # skipped references only return report_line and import_status
            report_line, import_status = result
            out = (report_line, import_status, None )
        elif len(result) == 3:
            # successfully imported references additionally return an object
            report_line, import_status, ob = result
            out = (report_line, import_status, ob )
            
        # This is just for clarity
        return out
                                                                                                            
    security.declareProtected(BIBFOLDER_ADD_CONTENT_PERMISSION, 'logImportReport')
    def logImportReport(self, report):
        """Store the import report.
        """
        # Just pass off the import report to the place that actually did the importing.
        # XXX Should have a security check here though!
        self.getAssociatedBibFolder().logImportReport(report)
                                                                                                                                                                                                    
registerType(BibliographyTopic, PROJECTNAME)
