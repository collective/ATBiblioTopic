Description

  This product is an add-on to Raphael Ritz's CMFBibliographyAT.
  It lets portal users organize existing bibliography references
  into lists.
  Smart Bibliography Lists can be displayed using one of the standard
  (file system based) bibliography styles shiped with the product,
  or using custom bibliography styles designed by protal users.

  It should not be too difficult for a python programmer to write its own
  file system based bibliography styles. If you do so, please share your
  interesting bibliography styles with the community.


What It Does

  * Installs the 'Smart Bibliography List' content type.

Requirements

  * Plone 2+ / Archetypes 1.2.5+
  
  * CMFBibliographyAT (svn.plone.org/svn/collective
    used to be cvs.sourceforge.net:/cvsroot/collective)

  * Epoz 0.8.x / kupu 1.3.x


Installation

  - First, add the product to Zope:

    * extract the product from its archive and move it to the Products directory of your Zope Instance.

  - Then, install the product in Plone:

    * Recommended (Plone way): use the 'QuickInstaller' Tool from the ZMI, or go to 'Plone Setup > Add/Remove Products' in the Plone User Interface. 
      Check the corresponding checkbox and click the 'install' button.

    * Alternate (CMF Manual way): create an external method at the root of your cmf portal and run it by clicking its 'test' tab.

    External Method parameters:

    - Id: InstallATBiblioTopic

    - Title: Install ATBiblioTopic (optional)

    - Module Name: InstallATBiblioTopic.Install

    - Function Name: install

Documentation

  More documentation can be found in the 'doc' folder of this product.


Licence

  see LICENCE.txt


Contact

  Mike Gabriel - m.gabriel(at)sunweavers(dot)net 

  or subscribe to the PloneBiblio mailing list:
  https://zaubberer.net/mailman/listinfo/plone-biblio


Changes

    0.1
    
        o none
    
    pre-0.1
    
        o none