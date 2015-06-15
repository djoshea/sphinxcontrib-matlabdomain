#!/usr/bin/env python
# coding: utf-8
# basic conf.py for `argdoc` unit test suite
import os
import datetime
import argdoc
import sphinx_rtd_theme

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


# -- General configuration ------------------------------------------------

master_doc = 'master_toctree'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'argdoc.ext',
    'numpydoc', 
]


# sphinx autodoc config -------------------------------------------------------

autodoc_default_flags = [
    "show-inheritance",
    "undoc-members",
    "special-members",
    "private-members",
    "inherited-members",
]
autodoc_member_order = "bysource"


# intersphinx config ------------------------------------------------------------
intersphinx_mapping = { "python" : ("http://docs.python.org",None),
                        }

# other -------------------------------------------------------------------------


# General information about the project.
project = u'argdoc_test'
copyright = u'2015, Joshua G. Dunn'

# Short version number, for |version|
version = str(argdoc.__version__)
# The full version, including alpha/beta/rc tags, for |release|
release = "%s-r%s" % (argdoc.__version__,str(datetime.date.today()).replace("-","_"))


# The suffix of source filenames.
source_suffix = '.rst'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# spying ---------------------------------------------------------------------
import codecs
def spy_on_docstring(app,what,name,obj,options,lines):
    """Event handler that writes docstrings to RST files before final translation
    to HTML/XML/ePub/whatever by the Builder. RST files are named
    ``DOCNAME_docstring.rst`` where `DOCNAME` is given by `name`. RST documents
    are put in the build directory.

    Parameters
    ----------
    app
        Sphinx application instance
    
    what : str
        Type of object (e.g. "module", "function", "class")
    
    name : str
        Fully-qualified name of object
    
    obj : object
        Object to skip or not
    
    options : object
        Options given to the directive, whose boolean properties are set to `True`
        if their corresponding flag was given in the directive

    lines : list
        List of strings encoding the module docstrings after `Sphinx`_ processing

    """
    funcname = app.config.argdoc_main_func
    if what == "module" and obj.__dict__.get(funcname,None) is not None:
        if obj.__dict__.get(funcname).__dict__.get("noargdoc",False) == False:
            filename = os.path.join(app.outdir,"%s_docstring.rst" % name)
            app.debug("Writing docstring for module %s to %s." % (name,filename))
            with codecs.open(filename,encoding="utf-8",mode="w") as fout:
                for n,line in enumerate(lines):
                    try:
                        if isinstance(line,str):
                            line = line.encode("utf-8")
                        
                        fout.write(line)
                        fout.write(u"\n")
                    except:
                        app.warn("Could not write out line %s of file %s." % (n,name))

            fout.close()

def setup(app):
    app.connect("argdoc-process-docstring",spy_on_docstring)
