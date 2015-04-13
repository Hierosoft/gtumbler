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

from gi.repository import Gtk, GObject

from . helpers import get_builder, show_uri, get_help_uri

BOX_WIDGETS = ['top', 'bottom', 'left', 'right']

class BoundingBoxView(Gtk.Viewport):
	"""
	Custom widget for handling all the bounding boxes of a page
	"""

	__gtype_name__ = "BoundingBoxView"
	
	__gsignals__ = {
		'box-changed' : (GObject.SIGNAL_RUN_FIRST,
						 None,
						 (int,) # @param: the new box index
						),
						
		'value-changed' : (GObject.SIGNAL_RUN_FIRST,
						   None,
						   ()
						  ),
	}
	
	def __new__(cls):
		"""Special static method that's automatically called by Python when 
		constructing a new instance of this class.
		
		Returns a fully instantiated BoundingBoxView object.
		"""
		builder = get_builder('BoundingBoxView')
		new_object = builder.get_object("bounding_box_view")
		new_object.finish_initializing(builder)
		return new_object

	def finish_initializing(self, builder):
		"""Called while initializing this instance in __new__

		finish_initializing should be called after parsing the UI definition
		and creating a BoundingBoxView object with it in order to finish
		initializing the start of the new BoundingBoxView instance.
		"""
		# Get a reference to the builder and set up the signals.
		self.builder = builder
		self.ui = builder.get_ui(self, True)
		
		self._bboxes = [[.0] * 4 for i in range(5)]
		
	def on_cbo_box_changed(self, widget, *args):
		n = widget.get_active()
		for widget, value in zip(BOX_WIDGETS, self._bboxes[n]):
			getattr(self.ui, 'spb_%s' % widget).set_value(value)
		self.emit('box-changed', n)

	def on_spb_bottom_value_changed(self, widget, *args):
		self._bboxes[self.ui.cbo_box.get_active()][1] = widget.get_value()
		self.emit('value-changed')

	def on_spb_left_value_changed(self, widget, *args):
		self._bboxes[self.ui.cbo_box.get_active()][2] = widget.get_value()
		self.emit('value-changed')

	def on_spb_right_value_changed(self, widget, *args):
		self._bboxes[self.ui.cbo_box.get_active()][3] = widget.get_value()
		self.emit('value-changed')

	def on_spb_top_value_changed(self, widget, *args):
		self._bboxes[self.ui.cbo_box.get_active()][0] = widget.get_value()
		self.emit('value-changed')
