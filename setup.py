#!/usr/bin/python3

""" A setup utility for the HTML editor.
"""
import distutils
from distutils.dir_util import copy_tree
from distutils.core import setup
import sys
from os import walk
from os.path import join

rootitems = ['README.txt', 'CHANGELOG.txt',
    'multicubewriteup.odt', 'multicubewriteup.pdf',
    'doc.sh']
resfilelist = []
docfilelist = []

for root, dirs, files in walk('openglresources'):
    if (len(files) > 0):
        for y in files:
            if (len(root) > 0):
                tmpfile = join(root, y)
            else:
                tmpfile = y
            resfilelist.append(tmpfile)

for root, dirs, files in walk('doc'):
    if (len(files) > 0):
        for y in files:
            if (len(root) > 0):
                tmpfile = join(root, y)
            else:
                tmpfile = y
            docfilelist.append(tmpfile)

setup(name='multicube',
      version='1.0',
      description='Python Multiple Cube OpenGL Demo',
      author='Edward Charles Eberle',
      author_email='eberdeed@eberdeed.net',
      url='www.eberdeed.net',
      packages=['pymulticube'],
      package_dir={'pymulticube' : 'pymulticube'},
      package_data={'pymulticube' : ['*.*']},
      data_files=([('/usr/bin', ['multicube.py']),
                  ('multicube', rootitems),
                  ('multicube/doc', docfilelist),
                  ('multicube/openglresources', resfilelist)
                  ])
     )
if len(sys.argv) >= 2 and sys.argv[1] == "install":
    copy_tree("doc", "/usr/share/doc/multicube-doc")
    copy_tree("openglresources", "/usr/share/openglresources")
