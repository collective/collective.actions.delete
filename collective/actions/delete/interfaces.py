# -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingencollectiveeb

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

from zope.interface import Interface

class IFolderDelete(Interface):
    """ define the default view for deletion  with confirmation """


class IAction(Interface):

    def view(self):
        """ return the default view for an access """

class IActionSuccess(IAction):

    """ define the action in success """

class IActionFailure(IAction):

    """ define the action in failure """

class IActionCancel(IAction):

    """ define the action in cancel """