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

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Poppler

#from gtumbler_lib import pdf
import PyPDF2 as pdf
from gtumbler_lib.helpers import enum

from gi.repository import Rsvg as rsvg

BOX_NAMES = ['artBox', 'bleedBox', 'cropBox', 'mediaBox', 'trimBox']

EditType = enum('NO_EDIT', 'BOUNDING_BOXES')

class Document(object):
	"""
	This class represents a single document
	"""

	def __init__(self, filename):
		self._filename = filename
		self._document = Poppler.Document.new_from_file("file://%s" % self._filename, None)
		self._fin = open(filename, 'rb')
		self._pdf_rd = pdf.PdfFileReader(self._fin)
		self._page = None
		self._bboxes = [[] for i in range(len(BOX_NAMES))]
		self.set_page(0)

	def close(self):
		"""
		Closes the current document nicely
		"""
		
		try:
			self._fin.close()
		except:
			pass

	def get_origin(self):
		"""
		Get the origin the page should be drawn at on the Cairo context
		"""
		
		return self._origin

	def set_page(self, page = None):
		"""
		Set the current page.
		
		@param page: The zero-based page number to set.
		"""
		
		if page != None and page != self._page:
			self._page_obj = self._document.get_page(page)
			paper = self._pdf_rd.getPage(page)
			left, bottom = paper.mediaBox.lowerLeft
			right, top = paper.mediaBox.upperRight

			self._width, self._height = float(right - left), float(top - bottom)
			for i, box_name in enumerate(BOX_NAMES):
				box = getattr(paper, box_name, None)
				if box:
					self._bboxes[i] = [self._height - float(box.upperRight[1]),
										float(box.lowerLeft[1]),
										float(box.lowerLeft[0]),
										self._width - float(box.upperRight[0])]

			self._origin = (float(paper.cropBox.lowerLeft[0]),
							self._height - float(paper.cropBox.upperRight[1]))
			self._page = page
		
	def render(self, cairo_context):
		"""
		Renders the current page on the passed cairo_context
		
		@param cairo_context: A cairo context to draw on
		"""
		
		self._page_obj.render(cairo_context)

	def get_page(self):
		"""
		Returns the current page number
		
		@return: The current zero-based page number
		"""
		
		return self._page

	def get_n_pages(self):
		"""
		Returns the document page count
		
		@return: The document page count
		"""
		
		if getattr(self, '_n_pages', None):
			return self._n_pages
		self._n_pages = self._document.get_n_pages()
		return self._n_pages

	def get_page_size(self):
		return self._width, self._height

	def get_title(self):
		return self._document.get_property("title")


class DocumentView(Gtk.DrawingArea):
	"""
	A Gtk.DrawingArea designed to handle document rendering inside a Gtk.Window
	"""
	
	__gtype_name__ = "DocumentView"
	
	__gsignals__ = {
		'document-changed' : (GObject.SIGNAL_RUN_FIRST,
							  None,
							  ()
							 ),
		
		'page-changed' : (GObject.SIGNAL_RUN_FIRST,
						  None, 
						  (int,) # @param: the new page number
						 ),

		'zoom' : (GObject.SIGNAL_RUN_FIRST,
						  None, 
						  (float,) # @param: the new zoom level (scale factor, 1 == 100%)
				 ),
	}
	
	def __init__(self, *args):
		super(DocumentView, self).__init__()
		self.document = None
		self._page_number = None     
		self.set_zoom(1)
		self._pad = 3
		self._edit_mode = EditType.NO_EDIT
		self._edit_mode_data = None
		
		self.connect('draw', self._on_expose_event)

		#self._draw_logo()

	def _draw_logo(self):
		"""Draws the application logo on the Document View"""
		
		cr = self.get_window().cairo_create()
		svg = rsvg.Handle.new_from_file('data/media/gtumbler.svg')
		svg.render_cairo(cr)

	def _on_expose_event(self, widget, cr):
		"""
		This is the central event. It is responsible for coordinating the drawing
		processes on the Document View
		"""
		
		### PREAMBLE ###
		
		# Initial logo, displayed when no documents are loaded
		if not self.document:
			self._draw_logo()
			return

		### DOCUMENT RENDERING ###

		#TODO: To probably make this faster use event to create a clipping area
		#      (http://www.pygtk.org/articles/cairo-pygtk-widgets/cairo-pygtk-widgets.htm)
		
		w, h = self.document.get_page_size()
		
		s = self.get_zoom()
		
		#cr = widget.get_window().cairo_create()        

		## Grey page shadow
		cr.set_source_rgb(.3, .3, .3)
		cr.rectangle(self._pad, self._pad, s * w, s * h)
		cr.fill()
		
		## White default page background
		cr.set_source_rgb(1, 1, 1)
		cr.rectangle(0, 0, s * w, s * h)
		cr.fill()
		
		## Black page contour
		cr.set_source_rgb(0, 0, 0)
		cr.set_line_width(.8)
		cr.rectangle(0, 0, s * w, s * h)
		cr.stroke()
		
		## Rendering of the current page
		#cr = widget.get_window().cairo_create()
		if s != 1:
			cr.scale(s, s)

		cr.translate(*self.document.get_origin())
		self.document.render(cr)
		
		### EDIT MODE HANDLING ###
		
		if self._edit_mode == EditType.BOUNDING_BOXES:
			## Bounding Boxes
			self.draw_rectangle()
		
		return True

	def close(self):
		"""Closes the current document, if any."""
		if self.document:
			self.document.close()
			self.document = None

	def draw_rectangle(self, rect, color):
		pass

	def get_best_fit(self):
		return getattr(self, '_best_fit', False)

	def get_state(self):
		return bool(self.document)

	def get_zoom(self):
		return self._zoom

	def open(self, filename):
		# Check if a document is already opened and if so close it
		self.close()
		
		# Open the new document
		self.document = Document(filename)
		self.emit('zoom', self.get_zoom())
		self.emit('document-changed')
		self.emit('page-changed', self.document.get_page())
		self.refresh()

	def page_first(self):
		if not self.document: return
		page = self.document.get_page()
		if page <= 0: return
		self.set_page(0)
		self.refresh()

	def page_last(self):
		if not self.document: return
		page = self.document.get_page()
		if page >= self.document.get_n_pages() - 1: return
		self.set_page(self.document.get_n_pages() - 1)
		self.refresh()

	def page_next(self):
		if not self.document: return
		page = self.document.get_page()
		if page >= self.document.get_n_pages() - 1: return
		self.set_page(page + 1)
		self.refresh()

	def page_previous(self):
		if not self.document: return
		page = self.document.get_page()
		if page <= 0: return
		self.set_page(page - 1)
		self.refresh()

	def refresh(self):
		if self.document:
			w, h = self.document.get_page_size()
			s = self.get_zoom()
			self.set_size_request(self._pad + int(w * s), self._pad + int(h * s))
		self.queue_draw()

	def set_best_fit(self, best_fit):
		self._best_fit = best_fit
		if best_fit:
			self._fit_page = False
			rect_sw = self.get_parent().get_parent().get_parent().get_allocation()
			w, h = self.document.get_page_size()
			self._zoom = (rect_sw.width - 2 * 6. - float(self._pad) - 2) / w
		self.refresh()

	def set_edit_mode(self, mode, data = None):
		self._edit_mode = mode
		self._edit_mode_data = data

	def set_fit_page(self, fit_page):
		self._fit_page = fit_page
		if fit_page:
			self._best_fit = False
			rect_sw = self.get_parent().get_parent().get_parent().get_allocation()
			w, h = self.document.get_page_size()
			sx = (rect_sw.width - 2 * 6. - float(self._pad) - 2) / w
			sy = (rect_sw.height - 2 * 6. - float(self._pad) - 2) / h
			self._zoom = min([sx, sy])
		self.refresh()

	def set_page(self, page):
		if page < 0 or page > self.document.get_n_pages() - 1: return
		self.document.set_page(page)
		self.emit('page-changed', page)

	def set_zoom(self, zoom):
		if zoom > 16 or zoom < .25: return
		self._zoom = zoom
		self.refresh()
		self.emit('zoom', self._zoom)

	def zoom_in(self, delta):
		self.set_zoom(self._zoom + delta)
		
	def zoom_out(self, delta):
		if self._zoom - delta > 0:
			self.set_zoom(self._zoom - delta)

