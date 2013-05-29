# -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import unicodedata
import transaction
from Acquisition import aq_parent, aq_inner
from ZODB.POSException import ConflictError
from OFS.interfaces import IObjectManager
from zope.interface import implements
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite
from zope.component import adapts
from plone.app.linkintegrity.exceptions import LinkIntegrityNotificationException
from zope.i18nmessageid import MessageFactory
from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFPlone.utils import getFSVersionTuple
from Products.CMFPlone.utils import transaction_note

from interfaces import IFolderDelete
from interfaces import IAction
from interfaces import IActionCancel
from interfaces import IActionSuccess
from interfaces import IActionFailure

_ = MessageFactory('plone')


class Action(object):

    implements(IAction)
    adapts(IObjectManager)

    def __init__(self, context):
        self.context = context

    def view(self):
        return self.context.restrictedTraverse('@@folder_contents')

    def __call__(self):
        return self.view()()


class ActionSuccess(Action):
    __module__ = __name__
    implements(IActionSuccess)
    adapts(IObjectManager)


class ActionFailure(Action):
    __module__ = __name__
    implements(IActionFailure)
    adapts(IObjectManager)


class ActionCancel(Action):
    __module__ = __name__
    implements(IActionCancel)
    adapts(IObjectManager)


class FolderDelete(BrowserView):
    __module__ = __name__
    implements(IFolderDelete)
    delete_confirmation = ViewPageTemplateFile('templates/confirmation.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.paths = None
        self.portal = getSite()
        self.utils = self.portal.plone_utils
        self.initializePaths()

    def initializePaths(self):
        form = self.request.form
        if 'paths' in form:
            paths = form['paths']
            # strip portal path from paths only when called from
            # folder_contents but not when called by submitting
            # to itself (confirmation screen)
            if 'confirm' in form and form['confirm'] == 'confirmed':
                self.paths = paths
            else:
                self.paths = [self.strip_portal_path(path) for path in paths]

    def strip_portal_path(self, path):
        portal_path = self.portal.getPhysicalPath()
        path = path.split('/')
        for id in portal_path:
            if id == path[0]:
                path.pop(0)
        return '/'.join(path)

    def action(self):
        """ return name of the view """
        return ('@@%s' % self.__name__)

    def titles(self):
        """ return paths """
        return self.paths

    def __call__(self):
        """ some documentation """
        if (self.paths is None):
            message = _(u'You must select at least one item.')
            self.utils.addPortalMessage(message)
            return IActionFailure(self.context)()
        # if not self submitted, return confirmation screen
        if ('form.button.Delete' not in self.request
            and 'form.button.Cancel' not in self.request):
            return self.delete_confirmation()
        elif 'form.button.Delete' in self.request:
            return self.delete_folder()
        elif 'form.button.Cancel' in self.request:
            return IActionCancel(self.context)()

    def delete_folder(self):
        """ delete objects """
        self.request.set('link_integrity_events_to_expect', len(self.paths))
        if getFSVersionTuple() > (4, 0):
            # Using the legacy method from Plone 4
            success, failure = self.utils.deleteObjectsByPaths(self.paths, REQUEST=self.request)
        else:
            ## Using custom method up to Plone 3
            success, failure = self.deleteObjectsByPaths(self.paths, REQUEST=self.request)
        if success:
            self.status = 'success'
            mapping = {u'items': ', '.join(success)}
            message = _(u'${items} deleted.', mapping=mapping)
            self.utils.addPortalMessage(message)
            view = IActionSuccess(self.context).view()
        if failure:
            failure_message = ', '.join([('%s (%s)' % (x,
                str(y))) for (x, y,) in failure.items()])
            message = _(u'${items} could not be deleted.',
                mapping={u'items': failure_message})
            self.utils.addPortalMessage(message, type='error')
            view = IActionFailure(self.context).view()
        return view()

    def deleteObjectsByPaths(self, paths, handle_errors=True, REQUEST=None):
        """Copy of deleteObjectsByPaths of the method of same name in
        ``Products.CMFPlone.PloneTool.PloneTool``.
        We just know that
        """
        failure = {}
        success = []
        # use the portal for traversal in case we have relative paths
        portal = getSite()
        traverse = portal.restrictedTraverse
        charset = getSiteEncoding(self.context)
        for path in paths:
            # Skip and note any errors
            if handle_errors:
                sp = transaction.savepoint(optimistic=True)
            try:
                obj = traverse(path)

                # Check for the case where a path to a nonexisting object
                # deletes an acquired object
                if path.startswith('/'):
                    absolute_path = path
                else:
                    portal_path = '/'.join(portal.getPhysicalPath())
                    absolute_path = "%s/%s" % (portal_path, path)
                if '/'.join(obj.getPhysicalPath()) != absolute_path:
                    raise
                # end check

                obj_parent = aq_parent(aq_inner(obj))
                obj_parent.manage_delObjects([obj.getId()])
                # PATCH: support for content with non ASCII chars
                title_or_id = obj.title_or_id()
                if not isinstance(title_or_id, unicode):
                    title_or_id = unicode(title_or_id, charset, 'ignore')
                # Transform in plain ASCII
                title_or_id = unicodedata.normalize('NFKD', title_or_id).encode('ascii','ignore')
                success.append('%s (%s)' % (title_or_id, path))
                # /PATCH
            except ConflictError:
                raise
            except LinkIntegrityNotificationException:
                raise
            except Exception, e:
                if handle_errors:
                    sp.rollback()
                    failure[path] = e
                else:
                    raise
        transaction_note('Deleted %s' % (', '.join(success)))
        return success, failure
