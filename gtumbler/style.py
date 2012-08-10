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

style = """
#tb_side {
    background-image: -gtk-gradient(linear,
                                    left top, left bottom,
                                    from (@bg_color),
                                    color-stop (.5, shade(white, .8)),
                                    to (white)
                                   )
}

#box_main GtkPaned {
    background-image: -gtk-gradient(linear, left top, left bottom,
                                    from (shade (red, .9)),
                                    color-stop (.5, shade (red, .65)),
                                    to (shade (red, .85))
                                   );
}

#lbl_right_pane_title {
    color: shade(red, 1.85);
}
"""
