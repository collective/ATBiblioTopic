from Products.Archetypes.public import BaseSchema, Schema, MetadataSchema
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import InAndOutWidget

from Products.CMFBibliographyAT.content.base import BaseEntrySchema

from Products.ATBiblioTopic.config import BIBLIOGRAPHY_EXTENDED_SCHEMATA
import string, types

BibEntryExtendedSchema = Schema((
))

BibEntryExtendedMetadataSchema = MetadataSchema((
    LinesField('copyrightDepartment',
        searchable=0,
        widget=InAndOutWidget(
            size=6,
            label='Involved Departments',
            label_msgid = "label_involveddepartments_researchsubproject",
            description="",
            description_msgid = "help_involveddepartments_researchsubproject",
            macro = "involveddepartments_inandoutwidget",
            helper_js = ('involveddepartments_inandout.js',),
            i18n_domain = 'atresearchproject',
        ),    
    ),
))


# Monkeypatch CMFBibliographyAT if you need extra (metadata) schema fields
# extra schema fields can provide more flexibility with catalog queries.
if BIBLIOGRAPHY_EXTENDED_SCHEMATA:
    _former_BaseEntrySchema = BaseEntrySchema
    BaseEntrySchema = _former_BaseEntrySchema + \
                      BibEntryExtendedSchema + \
                      BibEntryExtendedMetadataSchema 

    