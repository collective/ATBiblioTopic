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
from Products.Archetypes.public import DisplayList
from Products.CMFBibliographyAT.config import REFERENCE_TYPES
from Products.ATContentTypes.tool.topic import TopicIndex

GLOBALS = globals()
ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "ATBiblioTopic"
SKINS_DIR = 'skins'
ATBT_DIR = os.path.abspath(os.path.dirname(__file__))

ATBIBTOPIC_BIBFOLDER_REF = 'ATBiblioTopic_associated_bibfolder'
REFERENCE_ALLOWED_TYPES = [tn.replace(' Reference', 'Reference') for tn in REFERENCE_TYPES]
LISTING_VALUES = DisplayList((
    ('bulleted', 'Bulleted list'),
    ('ordered', 'Ordered list'),
    ('lines', 'Simple lines list'),
    ('table', 'Table listing'),
    ))

# do not touch this variable structure!!! unless you know what you are doing!!! actually do not touch anything in this file
try:
    import Products.TextIndexNG2
    # extra args for the TextIndexNG2 index to be added to portal_catalog, do not touch!!!
    ting2_extra = record()
    ting2_extra.indexed_fields   = ''
    ting2_extra.default_encoding = 'utf-8'
    ting2_extra.use_converters   = 1
    text_index_type = { 'type': 'TextIndexNG2', 'extra': ting2_extra, }
    
except ImportError
    # do not at all touch zcti_extra, it is needed to created ZCTextIndex catalog indexes
    zcti_extra = record()
    zcti_extra.lexicon_id = 'plone_lexicon'
    zcti_extra.index_type = 'Okapi BM25 Rank'
    zcti_extra.doc_attr   = None
    text_index_type = { 'type': 'ZCTextIndex', 'extra': zcti_extra, }
    
BIBLIOTOPIC_CRITERIAFIELDS = [
    {
	'field'		: ('SearchableText', 'Search all reference item text fields',
			   'This criterion looks at all searchable text passages in bibliographical reference items.', '', ),
        'index_type'    : text_index_type,
	'ctypes'	: ('ATSimpleStringCriterion', )
    },	
    {
	'field'		: ( 'publication_year', 'Publication year of the referenced bibliographical item',''),
        'index_type'    : { 'type': 'DateIndex', },
	'ctypes'	: ( 'ATDateRangeCriterion', 'ATFriendlyDateCriteria',)
    },	
    {
	'field'		: ('Title','Title of the referenced bibliography item',''),
        'index_type'    : text_index_type,
	'ctypes'	: ('ATSimpleStringCriterion',)
    },	
]
BIBLIOTOPIC_SORTFIELDS = [
    {
	'field'		: ( 'publication_year','Publication year of the referenced bibliographical item',''),
        'index_type'    : { 'type': 'DateIndex', },
	'ctypes'	: ('ATSortCriterion', 'ATDateRangeCriterion', 'ATFriendlyDateCriteria',)
    },	
#    {
#	'field'		: ('Author','Author of referenced bibliographical item',''),
#        'index_type'    : { 'type': 'FieldIndex', },
#	'ctypes'	: ('ATSortCriterion', 'ATDateRangeCriterion', 'ATFriendlyDateCriteria',)
#    },	
]

# generated from the BIBLIOTOPIC_CRITERIAFIELDS
CATALOG_INDEXES = [ dict([('name',criterion['field'][0])] + [ (key, criterion['index_type'][key]) for key in criterion['index_type'].keys() ]) for criterion in (BIBLIOTOPIC_CRITERIAFIELDS + BIBLIOTOPIC_SORTFIELDS) ]
CATALOG_METADATA = [ criterion['field'][0] for criterion in BIBLIOTOPIC_SORTFIELDS ]

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
                                                                                                            
                                                                                                            