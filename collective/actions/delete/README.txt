==========================================================
collective.actions.delete : delete items with confirmation
==========================================================

First log as portal administrator::

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> browser.handleErrors = False
    >>> browser.open('http://nohost/plone/')

    >>> browser.getLink('Log in').click()
    >>> 'submit' in browser.contents
    True
    >>> from Products.PloneTestCase.setup import portal_owner, default_password
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> 'Welcome! You are now logged in.' in browser.contents
    True

Now install collective.actions.delete::

    >>> report = self.portal.portal_setup.runAllImportStepsFromProfile('profile-collective.actions.delete:default')
    >>> report['messages'][u'actions']
    'actions: Actions tool imported.'


Secondly create some contents::

    >>> self.loginAsPortalOwner()
    >>> self.portal.invokeFactory('Document','document-1', title='Document 1')
    'document-1'

Go to folder contents and delete the content::

    >>> browser.open('http://nohost/plone/folder_contents')
    >>> 'Document 1' in browser.contents
    True
    >>> '@@folder_delete' in browser.contents
    True
    >>> browser.open('http://nohost/plone/@@folder_delete')
    >>> 'You must select at least one item' in browser.contents
    True


    >>> browser.open('http://nohost/plone/@@folder_delete?paths:list=/plone/document-1')
    >>> 'Do you really want to delete those contents ?' in browser.contents
    True
    >>> browser.getControl('Delete').click()
    >>> 'Document 1 (document-1) deleted.' in browser.contents
    True

Now test with two content (one is lock and one is removable)::

    >>> self.portal.invokeFactory('Document','document1', title='Document 1')
    'document1'
    >>> self.portal.invokeFactory('Document','document2', title='Document 2')
    'document2'


To lock document-2 we go to edit view::

    >>> browser.open('http://nohost/plone/document2/edit')

Ok and now we try to delete document1 and document2::

    >>> browser.open('http://nohost/plone/@@folder_delete?paths:list=/plone/document1&paths:list=/plone/document2')
    >>> 'Do you really want to delete those contents ?' in browser.contents
    True
    >>> browser.getControl('Delete').click()
    >>> 'Document 1 (document1) deleted.' in browser.contents
    True
    >>> 'document2 (Object "document2" is locked via WebDAV) could not be deleted.'  in browser.contents
    True

An issue mentioned by an user show that deleting a document with a non ASCII
title raise an Unicode Error.

    >>> self.portal.invokeFactory('Document', 'document3', title=u'Doc\xfcment 3')
    'document3'
    >>> self.portal['document3'].Title()
    'Doc\xc3\xbcment 3'

Yes the title created in Unicode is now in utf-8 (?) Now we try to delete that
new document.

    >>> browser.open('http://nohost/plone/@@folder_delete?paths:list=/plone/document3')
    >>> 'Do you really want to delete those contents ?' in browser.contents
    True
    >>> browser.getControl('Delete').click()
    >>> 'Doc\xc3\xbcment 3 1 (document3) deleted.' in browser.contents
    True
