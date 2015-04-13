# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2012 Gabriele N. Tornetta <phoenix1987@gmail.com>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

# This is your preferences dialog.
#
# Define your preferences in
# data/glib-2.0/schemas/net.launchpad.gtumbler.gschema.xml
# See http://developer.gnome.org/gio/stable/GSettings.html for more info.

from gi.repository import Gio # pylint: disable=E0611

import gettext
from gettext import gettext as _
gettext.textdomain('gtumbler')

import logging
logger = logging.getLogger('gtumbler')

from gtumbler_lib.PreferencesDialog import PreferencesDialog

class PreferencesGtumblerDialog(PreferencesDialog):
    __gtype_name__ = "PreferencesGtumblerDialog"

    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the preferences dialog"""
        super(PreferencesGtumblerDialog, self).finish_initializing(builder)

        # Bind each preference widget to gsettings
        settings = Gio.Settings.new("net.launchpad.gtumbler")
        widget = self.builder.get_object('chk_display_path')
        settings.bind("example", widget, "active", Gio.SettingsBindFlags.DEFAULT)

        # Code for other initialization actions should be added here.
