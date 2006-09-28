##########################################################################
#                                                                        #
#              copyright (c) 2006 +++ sunweavers.net +++                 #
#                                 and contributors                       #
#                                                                        #
#     maintainers: Mike Gabriel, m.gabriel@sunweavers.net                #
#                                                                        #
##########################################################################

""" Product configuration
"""

import os
from Products.CMFCore.permissions import AddPortalContent
from Products.Archetypes.public import DisplayList
from Products.CMFBibliographyAT.config import REFERENCE_TYPES
from Products.ATContentTypes.tool.topic import TopicIndex
from ZPublisher.HTTPRequest import record

GLOBALS = globals()
ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "ATBiblioTopic"
SKINS_DIR = 'skins'
ATBT_DIR = os.path.abspath(os.path.dirname(__file__))

ATBIBLIOTOPIC_BIBFOLDER_REF = 'ATBiblioTopic_associated_bibfolder'
REFERENCE_ALLOWED_TYPES = [tn.replace(' Reference', 'Reference') for tn in REFERENCE_TYPES]

LISTING_VALUES = DisplayList((
    ('bulleted', 'Bulleted list'),
    ('ordered', 'Ordered list'),
    ('lines', 'Simple lines list'),
    ('table', 'Table listing'),
    ))

try: 
    from Products.CMFBibliographyAT_extended_schemata.config import BIBLIOTOPIC_EXTENDEDSCHEMATA_STRUCTURAL_LAYOUT
except ImportError:
    BIBLIOTOPIC_EXTENDEDSCHEMATA_STRUCTURAL_LAYOUT = []

STRUCTURAL_VALUES = DisplayList(tuple([
    ('none','No Substructuring'),
    ('publication_year', 'Publication Year'),
    ('portal_type', 'Reference Type'),
    ('Authors', 'Authors\' Names'),
    ]
    + BIBLIOTOPIC_EXTENDEDSCHEMATA_STRUCTURAL_LAYOUT
    ))

# monkey patch section
BIBLIOGRAPHY_EXTENDED_SCHEMATA = True

# do not touch this variable structure!!! unless you know what you are doing!!! actually do not touch anything in this file
try:
    import Products.TextIndexNG2
    # extra args for the TextIndexNG2 index to be added to portal_catalog, do not touch!!!
    ting2_extra = record()
    ting2_extra.indexed_fields   = ''
    ting2_extra.default_encoding = 'utf-8'
    ting2_extra.use_converters   = 0
    text_index_type = { 'type': 'TextIndexNG2', 'extra': ting2_extra, }
    
except ImportError:
    # do not at all touch zcti_extra, it is needed to created ZCTextIndex catalog indexes
    zcti_extra = record()
    zcti_extra.lexicon_id = 'plone_lexicon'
    zcti_extra.index_type = 'Okapi BM25 Rank'
    zcti_extra.doc_attr   = None
    text_index_type = { 'type': 'ZCTextIndex', 'extra': zcti_extra, }
    
try: 
    from Products.CMFBibliographyAT_extended_schemata.config import BIBLIOTOPIC_EXTENDEDSCHEMATA_CRITERIAFIELDS
except ImportError:
    BIBLIOTOPIC_EXTENDEDSCHEMATA_CRITERIAFIELDS = []

BIBLIOTOPIC_CRITERIAFIELDS = [
    {
	'field'		: ('SearchableText', 'Search all reference item text fields',
			   'This criterion looks at all searchable text passages in bibliographical reference items.', '', ),
	'ctypes'	: ('ATSimpleStringCriterion', ),
    },	
    {
	'field'		: ('getAuthors','Authors','Author of referenced bibliographical item',''),
        'catalog'       : True,
        'custom_view'   : True,                   
        'index_type'    : text_index_type,
	'ctypes'	: ( 'ATSimpleStringCriterion',),
    },	
    {
	'field'		: ( 'publication_date', 'Publication Date', 'Publication date of the referenced bibliographical item',),
        'custom_view'   : True,                   
	'ctypes'	: ( 'ATDateRangeCriterion', 'ATFriendlyDateCriteria',),
    },	
    {
	'field'		: ('Title','Title', 'Title of the referenced bibliography item',''),
        'custom_view'   : True,                   
	'ctypes'	: ('ATSimpleStringCriterion',),
    },	
    {
	'field'		: ('path','Website Path', 'Select specific subtrees of your site to be searched for bibliographical items',''),
        'custom_view'   : True,                   
	'ctypes'	: ('ATPathCriterion',),
    },	
    {
	'field'		: ('portal_type','Reference Type(s)', 'Select reference types that you want to include into your smart bibliography list',''),
        'custom_view'   : True,                   
	'ctypes'	: ('ATPortalTypeCriterion',),
    },	    
] + BIBLIOTOPIC_EXTENDEDSCHEMATA_CRITERIAFIELDS
BIBLIOTOPIC_SORTFIELDS = [
    {
	'field'		: ( 'publication_year', 'Publication Year', 'Publication year of the referenced bibliographical item',),
	'ctypes'	: ('ATSortCriterion',),
    },	
    {
	'field'		: ('Authors','Authors', 'Author(s) of referenced bibliographical item',),
	'ctypes'	: ('ATSortCriterion', ),
    },	
    {
	'field'		: ('sortable_title','Title', 'Title of the referenced bibliography item',''),
	'ctypes'	: ('ATSortCriterion',),
    },	
]

# generated from the BIBLIOTOPIC_CRITERIAFIELDS
CATALOG_INDEXES = [ dict([('name',criterion['field'][0])] + [ (key, criterion['index_type'][key]) for key in criterion['index_type'].keys() ]) for criterion in (BIBLIOTOPIC_CRITERIAFIELDS + BIBLIOTOPIC_SORTFIELDS) if criterion.has_key('catalog') and criterion['catalog'] ]
CATALOG_METADATA = [ criterion['field'][0] for criterion in BIBLIOTOPIC_SORTFIELDS if criterion.has_key('catalog') and criterion['catalog'] ]

# initializing criteria indexes for BiblioTopics
BIBLIOTOPIC_INDEXES = {}
for crit_field in BIBLIOTOPIC_CRITERIAFIELDS + BIBLIOTOPIC_SORTFIELDS:
    index = {}
    index_name = crit_field['field'][0]
    index['friendlyName'] = crit_field['field'][1]
    index['description'] = crit_field['field'][2]
    index['criteria'] = crit_field['ctypes']
    indexObj = TopicIndex(index_name, **index)
    BIBLIOTOPIC_INDEXES[index_name] = indexObj
                                    