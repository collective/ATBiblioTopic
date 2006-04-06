try:

  from Products.LinguaPlone.public import listTypes
except:
  # no multilingual support
  from Products.Archetypes.public import listTypes
  
from Products.Archetypes.Extensions.utils import installTypes, install_subskin

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.CatalogTool import _eioRegistry

from Products.ATBiblioTopic.config import PROJECTNAME
from Products.ATBiblioTopic.config import GLOBALS
from Products.ATBiblioTopic.config import CATALOG_INDEXES
from Products.ATBiblioTopic.config import CATALOG_METADATA

from StringIO import StringIO

def addToFactoryTool(self, out):
    # make new types use portal_factory
    ftool = getToolByName(self, 'portal_factory')
    if ftool:
	portal_factory_types = ftool.getFactoryTypes().keys()
	for portalType in [ typeDict['portal_type'] for typeDict in listTypes(PROJECTNAME) ]:
    	    if portalType not in portal_factory_types:
		portal_factory_types.append(portalType)
        ftool.manage_setPortalFactoryTypes(listOfTypeIds=portal_factory_types)
	print >> out, 'New types use portal_factory'

def addIndexesToCatalogTool(self, out):
    ctool = getToolByName(self, 'portal_catalog')
    if ctool:
        # add indexes and metadatas to the portal catalog
        ct = getToolByName(self, 'portal_catalog')
        print CATALOG_INDEXES
        for idx in CATALOG_INDEXES:
            if idx['name'] in ct.indexes():
	        ct.delIndex(idx['name'])
		ct.addIndex(**idx)
		ct.reindexIndex(idx['name'], REQUEST=None)
		out.write("Found the '%s' index in the catalog, reinstalled and reindexed it to make sure the index type correct.\n" % idx['name'])
	    else:
		ct.addIndex(**idx)
		ct.reindexIndex(idx['name'], REQUEST=None)
		out.write("Added and reindexed '%s' (%s) to the catalog.\n" % (idx['name'], idx['type']))
		    
def addMetadataToCatalogTool(self, out):
    ctool = getToolByName(self, 'portal_catalog')
    if ctool:
        # add indexes and metadatas to the portal catalog
        ct = getToolByName(self, 'portal_catalog')
        for entry in CATALOG_METADATA:
	    if entry in ct.schema():
	        out.write("Found '%s' in the catalog metadatas, nothing changed.\n" % entry)
	    else:
	        ct.addColumn(entry)
	        out.write("Added '%s' to the catalog metadatas.\n" % entry)

def install(self):
    out = StringIO()
 
    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
    out.write('%s\n' % listTypes(PROJECTNAME))
    addToFactoryTool(self, out)
    addIndexesToCatalogTool(self, out)
    addMetadataToCatalogTool(self, out)
    
    install_subskin(self, out, GLOBALS)

    out.write("Successfully installed %s." % PROJECTNAME)
    return out.getvalue()

def removeIndexesFromCatalogTool(self, out):
    ct = getToolByName(self, 'portal_catalog')
    if ct:
        # add indexes and metadatas to the portal catalog
        for idx in CATALOG_INDEXES:
            if idx['name'] in ct.indexes():
	        ct.delIndex(idx['name'])
		out.write("Removed '%s' index from the catalog.\n" % idx['name'])
	    else:
		out.write("Index '%s' (%s) not found in the catalog, nothing changed.\n" % (idx['name'], idx['type']))
		
def unregisterIndexableAtrributes(self, out):
    # unregister SearchableAuthors as callable
    #unregisterIndexableAttribute('SearchableAuthors')	
        
def removeMetadataFromCatalogTool(self, out):
    ct = getToolByName(self, 'portal_catalog')
    if ct:
        # add indexes and metadatas to the portal catalog
        for entry in CATALOG_METADATA:
	    if entry in ct.schema():
	        ct.delColumn(entry)
		out.write("Found '%s' in the catalog metadatas, removed it.\n" % entry)
	    else:
	        ct.addColumn(entry)
	        out.write("Column '%s' has not been found in the catalog metadatas. Nothing changed.\n" % entry)
									  
def uninstall(self):
    out = StringIO()
    removeIndexesFromCatalogTool(self, out)
    removeMetadataFromCatalogTool(self, out)
    unregisterIndexableAtrributes(self, out)
    # all the rest of cleaning we leave to the quickinstaller
    print >> out, "Uninstalled %s." % PROJECTNAME
    return out.getvalue()
    