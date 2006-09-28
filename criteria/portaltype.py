#
# ATBiblioTopic monkeypatches ATPortalTypeCriterion
#

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.criteria import ATPortalTypeCriterion

def getATBibliographyTopicCurrentValues(self):

    topic_meta_type = self.aq_inner.aq_parent.aq_base.meta_type
    if topic_meta_type and topic_meta_type == 'ATBibliographyTopic':
	bib_tool = getToolByName(self, 'portal_bibliography')
	ref_types = bib_tool.getReferenceTypes()
	ref_types.sort()
	return ref_types
	
    else:
	return ATPortalTypeCriterion._former_getCurrentValues(self)	
		
ATPortalTypeCriterion._former_getCurrentValues = ATPortalTypeCriterion.getCurrentValues
ATPortalTypeCriterion.getCurrentValues = getATBibliographyTopicCurrentValues
print '***'
print '*** ATBiblioTopic monkey-patched ATContentTypes\' ATPortalTypeCriterion'
print '***'