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

from Products.Archetypes.public import DisplayList
from Products.CMFBibliographyAT.config import REFERENCE_TYPES

ATBIBLIST_BIBFOLDER_REF = 'ATBiblioList_associated_bibfolder'

REFERENCE_ALLOWED_TYPES = [tn.replace(' Reference', 'Reference') for tn in REFERENCE_TYPES]

LISTING_VALUES = DisplayList((
    ('bulleted', 'Bulleted list'),
    ('ordered', 'Ordered list'),
    ('lines', 'Simple lines list'),
    ('table', 'Table listing'),
    ))

