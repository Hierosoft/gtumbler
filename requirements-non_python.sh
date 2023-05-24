#!/bin/bash
# cat readme-dev.md
sudo dnf install gobject-introspection-devel
# ^ pulls in gobject-introspection python3-markdown
# ^ as recommended by next line (in error that occurs otherwise)
python2 -m pip install PyGObject
# Still says
# File "/home/owner/.local/lib/python2.7/site-packages/gi/module.py", line 132, in __getattr__
#     self.__name__, name))
# AttributeError: 'gi.repository.Gtk' object has no attribute 'Container'
