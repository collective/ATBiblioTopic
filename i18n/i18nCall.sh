#!/bin/bash
cd ..
i18ndude rebuild-pot --pot i18n/atbibliotopic-generated.pot --create atbibliotopic --merge i18n/atbibliotopic-manual.pot ./skins
#i18ndude rebuild-pot --pot i18n/plone-generated.pot --create plone --merge i18n/plone-manual.pot ./skins
cp i18n/plone-manual.pot i18n/plone-generated.pot
cd i18n