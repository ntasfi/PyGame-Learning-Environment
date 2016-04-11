import sys
import os
from mock import Mock
sys.modules['pygame'] = Mock()
sys.modules['pygame.constants'] = Mock()

#so we can import ple
sys.path.append(os.path.join(os.path.dirname(__name__), ".."))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'numpydoc'
]

numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

# General information about the project.
project = u'PyGame Learning Environment'
copyright = u'2016, Norman Tasfi'
author = u'Norman Tasfi'

import ple

version = u'0.1.dev1'
# The full version, including alpha/beta/rc tags.
release = u'0.1.dev1'

language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'

todo_include_todos = False

#from lasagne!
if os.environ.get('READTHEDOCS') != 'True':
    try:
        import sphinx_rtd_theme
    except ImportError:
        pass  # assume we have sphinx >= 1.3
    else:
        html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
    
    html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']

htmlhelp_basename = 'PyGameLearningEnvironmentdoc'

latex_elements = {
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'PyGameLearningEnvironment.tex', u'PyGame Learning Environment Documentation',
     u'Norman Tasfi', 'manual'),
]

man_pages = [
    (master_doc, 'pygamelearningenvironment', u'PyGame Learning Environment Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'PyGameLearningEnvironment', u'PyGame Learning Environment Documentation',
     author, 'PyGameLearningEnvironment', 'RL for all.',
     'Miscellaneous'),
]
