import sys
import os

sys.path.append(os.path.abspath('..'))
project = 'Fast API Users and Contacts'
copyright = '2023, GFour'
author = 'GFour'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']







