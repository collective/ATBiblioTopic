## Script (Python) "getXMLSelectVocab"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=vocab_method,param,value
##title=Get a DisplayList and format fot XML request

params = {param:value}

try:
   vocab = getattr(context, vocab_method)(**params)
except AttributeError:
   vocab = context.restrictedTraverse("@@%s" % vocab_method)(**params)

RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-Type', 'text/xml;charset=utf-8')
translate = context.translate

results = [(translate(vocab.getValue(item)), item) for item in vocab]

item_strings = [u'^'.join(a) for a in results]
result_string = u'|'.join(item_strings)

return "<div>%s</div>" % result_string.encode('utf-8')

#return "<div>Hello!</div>"