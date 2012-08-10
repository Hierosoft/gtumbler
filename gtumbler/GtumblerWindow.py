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

import gettext
from gettext import gettext as _
gettext.textdomain('gtumbler')

from gi.repository import Gtk # pylint: disable=E0611
from gi.repository import Gdk # pylint: disable=E0611
import logging
logger = logging.getLogger('gtumbler')

from gtumbler_lib import Window
from gtumbler_lib.DocumentView import DocumentView
from gtumbler_lib.BoundingBoxView import BoundingBoxView
from gtumbler_lib.ActionContext import ActionContext
from gtumbler_lib.helpers import enum
from gtumbler.AboutGtumblerDialog import AboutGtumblerDialog
from gtumbler.PreferencesGtumblerDialog import PreferencesGtumblerDialog

from style import style

import rsvg

RightPaneType = enum('BOUNDING_BOXES')

# See gtumbler_lib.Window.py for more details about how this class works
class GtumblerWindow(Window):
    __gtype_name__ = "GtumblerWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(GtumblerWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutGtumblerDialog
        self.PreferencesDialog = PreferencesGtumblerDialog

        # Code for other initialization actions should be added here.

        # Styling
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(style)
        context = Gtk.StyleContext()
        context.add_provider_for_screen(Gdk.Screen.get_default(),
                                        css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER) 
        self.ui.tb_main.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        for widget in self.ui._widget_dict:
            getattr(self.ui._widget_dict[widget], 'set_name', lambda a: None)(widget)

        # Managing Action Contexts
        self.ac_document_opened = ActionContext()
        self.ac_document_opened.append(self.ui.action_bounding_boxes)

        # Installing the BoundingBoxView widget
        self.ui.bounding_box_view = BoundingBoxView()
        self.ui.bounding_boxes.add(self.ui.bounding_box_view)

        # Connecting signals for the Document View
        self.ui.da_doc_view.connect('document-changed', self.on_da_doc_view_document_changed)
        self.ui.da_doc_view.connect('page-changed', self.on_da_doc_view_page_changed)
        self.ui.da_doc_view.connect('zoom', self.on_da_doc_view_zoom)
        
        # Connecting signals for the Bounding Box View
        self.ui.bounding_box_view.connect('box-changed', self.on_bounding_box_view_box_changed)
        self.ui.bounding_box_view.connect('value-changed', self.on_bounding_box_view_value_changed)
    
    ### BEGIN HELPERS

    def lock_paned2(self):
        self.ui.paned2.child_set_property(self.ui.paned2.get_child2(), 'shrink', True)
        self.ui.paned2.set_position(9999)

    def release_paned2(self):
        self.ui.paned2.child_set_property(self.ui.paned2.get_child2(), 'shrink', False)
        self.ui.paned2.set_position(9998)

    def reposition_after_zoom(self, x, y, s):
        ax = self.ui.sw_doc_view.get_hadjustment().get_value()
        ay = self.ui.sw_doc_view.get_vadjustment().get_value()
        s = self.ui.da_doc_view.get_zoom() / s
        ax = ax + (s - 1) * (x - 6)
        ay = ay + (s - 1) * (y - 6)
        
        try:
            self.ui.sw_doc_view.get_hadjustment().set_value(ax)
        except:
            print "H panick"

        try:
            self.ui.sw_doc_view.get_vadjustment().set_value(ay)
        except:
            print "V panick"

    def reposition_at_middle(self, s):
        x = 6 + self.ui.sw_doc_view.get_hadjustment().get_value() \
              + self.ui.sw_doc_view.get_hadjustment().get_page_size() / 2

        y = 6 + self.ui.sw_doc_view.get_vadjustment().get_value() \
              + self.ui.sw_doc_view.get_vadjustment().get_page_size() / 2

        self.reposition_after_zoom(x, y, s)

    def toggle_zoom(self, active):
        self.ui.tb_main_zoom_best_fit.set_active(active)
        self.ui.tb_main_zoom_fit_page.set_active(active)

    ### END HELPERS



    ### BEGIN SIGNAL HANDLERS

    def on_action_open_activate(self, action, *args):
        open_dialog = Gtk.FileChooserDialog("Select a document", self,
											buttons = (Gtk.STOCK_OK,
                                                       Gtk.ResponseType.OK,
													   Gtk.STOCK_CANCEL,
                                                       Gtk.ResponseType.CANCEL))

        ret = open_dialog.run()
        if ret == Gtk.ResponseType.OK:
            try:
                self.ui.da_doc_view.open(open_dialog.get_filename())
                self.ac_document_opened.set_sensitive(True)
            except:
                pass # TODO: Add notification of failure
        open_dialog.destroy()

    def on_bounding_box_view_box_changed(self, widget, new_box):
        pass

    def on_bounding_box_view_value_changed(self, widget, *args):
        pass

    def on_btn_right_pane_close_clicked(self, widget, *args):
        self.lock_paned2()

    def on_da_doc_view_button_press_event(self, widget, event, *args):
        pass

    def on_da_doc_view_document_changed(self, widget):
        self.ui.lbl_n_pages.set_text("%d " % widget.document.get_n_pages())

    def on_da_doc_view_page_changed(self, widget, new_page):
        self.ui.txt_page.set_text(str(new_page + 1))

    def on_da_doc_view_scroll_event(self, widget, event, *args):
        if event.type == Gdk.EventType.SCROLL and Gdk.ModifierType.CONTROL_MASK & event.state:
            if self.ui.da_doc_view.get_state():
                s = self.ui.da_doc_view.get_zoom()

                if event.direction == Gdk.ScrollDirection.UP:
                    self.ui.da_doc_view.zoom_in(0.25)
                elif event.direction == Gdk.ScrollDirection.DOWN:
                    self.ui.da_doc_view.zoom_out(0.25)
                self.reposition_after_zoom(event.x, event.y, s)

            return True

    def on_da_doc_view_zoom(self, widget, zoom):
        self.ui.txt_zoom.set_text('%d %%' % int(zoom * 100))

    def on_da_tumbler_draw(self, widget, event, *args):
        # Showing the tumbler shadow
        cr = widget.get_window().cairo_create()
        svg = rsvg.Handle(file='data/media/tumbler.svg')
        svg.render_cairo(cr)

    def on_action_bounding_boxes_activate(self, widget, *args):
        self.ui.lbl_right_pane_title.set_markup('<b>Bounding Boxes</b>')
        self.ui.nb_right_pane.set_current_page(RightPaneType.BOUNDING_BOXES)
        self.release_paned2()

    def on_paned1_button_press_event(self, widget, event, *args):
        return not self.ui.tb_sidepane.get_active()

    def on_paned2_button_press_event(self, widget, event, *args):
        try:
            return not self.ui.nb_right_pane.get_window().is_visible()
        except:
            return True
  
    def on_tb_main_first_clicked(self, widget, *args):
        self.ui.da_doc_view.page_first()  

    def on_tb_main_last_clicked(self, widget, *args):
        self.ui.da_doc_view.page_last()
    
    def on_tb_main_next_clicked(self, widget, *args):
        self.ui.da_doc_view.page_next()

    def on_tb_main_prev_clicked(self, widget, *args):
        self.ui.da_doc_view.page_previous()  

    def on_tb_main_zoom_best_fit_toggled(self, widget, *args):
        self.ui.da_doc_view.set_best_fit(widget.get_active())
        if widget.get_active():
            self.ui.tb_main_zoom_fit_page.set_active(False)
    
    def on_tb_main_zoom_fit_page_clicked(self, widget, *args):
        self.ui.da_doc_view.set_fit_page(widget.get_active())
        if widget.get_active():
            self.ui.tb_main_zoom_best_fit.set_active(False)

    def on_tb_main_zoom_in_clicked(self, widget, *args):
        s = self.ui.da_doc_view.get_zoom()
        self.ui.da_doc_view.zoom_in(0.25)
        self.reposition_at_middle(s)
        self.toggle_zoom(False)

    def on_tb_main_zoom_out_clicked(self, widget, *args):
        s = self.ui.da_doc_view.get_zoom()
        self.ui.da_doc_view.zoom_out(0.25)
        self.reposition_at_middle(s)
        self.toggle_zoom(False)

    ### END SIGNAL HANDLERS
