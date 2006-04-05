## Script (Python) "listDownload"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=format='BiBTex'
##title=
##
request = container.REQUEST
RESPONSE =  request.RESPONSE

if not format: return None

RESPONSE.setHeader('Content-Type', 'application/octet-stream')
RESPONSE.setHeader('Content-Disposition',
                   'attachment; filename=%s' %\
                   context.getId() + '.' + format)

bibtool = context.portal_bibliography
output = ''
brains = context.queryCatalog()
for brain in brains:
    obj = brain.getObject()
    output += bibtool.render(obj, format)

return output
    
