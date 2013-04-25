########################
sphinxcontrib.paverutils
########################

This module provides an alternative integration of Sphinx and
Paver_. It supports calling Sphinx from within Paver using multiple
configurations, and does not assume you only want to build HTML
output.

Basic Usage
===========

To use this module, import it in your pavement.py file as ``from
sphinxcontrib import paverutils``, then define option Bundles for
"html" and/or "pdf" output using the options described in the task
help.

For example::

    import paver
    import paver.misctasks
    from paver.path import path
    from paver.easy import *
    import paver.setuputils
    paver.setuputils.install_distutils_tasks()
    try:
        from sphinxcontrib import paverutils
    except:
        import warnings
        warnings.warn('sphinxcontrib.paverutils was not found, you will not be able to produce documentation')

    options(
        setup=Bunch(
            name = 'MyProject',
            version = '1.0',

            # ... more options here ...
            ),

        # Defaults for sphinxcontrib.paverutils
        sphinx = Bunch(
            docroot='.',
            sourcedir='docsource',
            builder='html',
        ),

        # One configuration to build HTML for the package
        html=Bunch(
            builddir='docs',
            confdir='sphinx/pkg',
        ),

        # Another configuration with different templates
        # to build HTML to upload to the website
        website=Bunch(
            builddir = 'web',
            confdir='sphinx/web',
        ),

        # We also want a PDF file for the website,
        # so the instructions are included in the web
        # configuration directory.
        pdf=Bunch(
            builddir='web',
            builder='latex',
            confdir='sphinx/web',
        ),

    )

Tasks
=====

After you have imported ``sphinxcontrib.paverutils`` in your
``pavement.py`` file, Paver will show two additional tasks.  ``html``
takes the place of the task defined in ``paver.doctools`` and can be
used to build HTML output.  ``pdf`` uses the LaTeX builder and an
external toolset such as TeXLive_ to create a PDF manual.

Configuration Parameters
========================

docroot
  the root under which Sphinx will be working.
  
  default: ``docs``

builddir
  directory under the docroot where the resulting files are put.

  default: ``build``

sourcedir
  directory under the docroot for the source files

  default: ``""`` (empty string)

doctrees
  the location of the cached doctrees

  default: ``$builddir/doctrees``

confdir
  the location of the sphinx conf.py

  default: ``$sourcedir``

outdir
  the location of the generated output files

  default: ``$builddir/$builder``

builder
  the name of the sphinx builder to use

  default: ``html``

template_args
  dictionary of values to be passed as name-value pairs to the HTML
  builder

  default: ``{}``


Advanced Usage
==============

You can also develop your own tasks by calling ``run_sphinx()`` directly::

    @task
    @needs(['cog'])
    @cmdopts([
        ('in-file=', 'b', 'Blog input filename'),
        ('out-file=', 'B', 'Blog output filename'),
    ])
    def blog(options):
        """Generate the blog post version of the HTML for the current module.
        """
        # Generate html from sphinx
        paverutils.run_sphinx(options, 'blog')

        blog_file = path(options.blog.outdir) / options.blog.out_file
        dry("Write blog post body to %s" % blog_file,
            gen_blog_post,
            outdir=options.blog.outdir,
            input_base=options.blog.in_file,
            blog_base=options.blog.out_file,
            )

        if 'EDITOR' in os.environ:
            sh('$EDITOR %s' % blog_file)
        return


Cog Extensions
==============

In addition to the ``html`` and ``pdf`` tasks, the package includes the function ``run_script()`` to be used with cog to insert the output of a command line program in your documentation.

This example of reStructuredText source using ``run_script()``::

    .. {{{cog
    .. cog.out(run_script(cog.inFile, 'anydbm_whichdb.py'))
    .. }}}
    .. {{{end}}}

renders to::

    .. {{{cog
    .. cog.out(run_script(cog.inFile, 'anydbm_whichdb.py'))
    .. }}}

    ::

    	$ python anydbm_whichdb.py
    	dbhash

    .. {{{end}}}

The lines prefixed with ``..`` are comments, and do not appear in the
final HTML or PDF output.

Arguments:

input_file
  The name of the file being processed by cog.  Usually passed as cog.inFile.

script_name
  The name of the Python script living in the same directory as input_file to be run.
  If not using an interpreter, this can be a complete command line.  If using an
  alternate interpreter, it can be some other type of file.

interpreter='python'
  The external interpreter to use for the program.  Specify 'python',
  'python3', 'jython', etc.

include_prefix=True
  Boolean controlling whether the ``::`` prefix is included. When chaining multiple
  commands together, the first instance would typically use the default and subsequent
  calls would use False.

ignore_error=False
  Boolean controlling whether errors are ignored.  If not ignored, the error
  is printed to stdout and then the command is run *again* with errors ignored
  so that the output ends up in the cogged file.

trailing_newlines=True
  Boolean controlling whether the trailing newlines are added to the output.
  If False, the output is passed to rstrip() then one newline is added.  If
  True, newlines are added to the output until it ends in 2.

break_lines_at=0
  Integer indicating the length where lines should be broken and
  continued on the next line.  Defaults to 0, meaning no special
  handling should be done.

line_break_mode='break'
  Mode to control how the line breaks are inserted.  Options are:

    'break'
      Insert the newline.
    'wrap'
      Use the textwrap module to wrap each line individually to the
      specified width.
    'fill'
      Use the textwrap module to wrap each line individually,
      inserting an appropriate amount of whitespace to keep the left
      edge of the lines aligned.
    'continue'
      Insert a backslash (``\``) and then a newline to break the line.
    'truncate'
      Break the line at the indicated location and discard the
      remainder.


.. note::

    PyMOTW_ makes heavy use of this function, with several variations in arguments, so
    refer to the source there for more examples if you need them.

Users
=====

PyMOTW_
    The Python Module of the Week package is built using Paver and
    Sphinx, including three forms of HTML and a PDF.

virtualenvwrapper_
    The documentation for virtualenvwrapper includes the packaged HTML
    and a website using alternate templates.

.. _Paver: http://www.blueskyonmars.com/projects/paver/

.. _PyMOTW: http://www.doughellmann.com/PyMOTW/

.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/

.. _TeXLive: http://tug.org/texlive/


History
=======

1.4
---

- Add different modes for breaking lines in the output of ``run_script()``.  

- Incorporate a fix from Maciek Starzyk for issue #6 so docroot can be
  set to something other than ``.``.

1.3
---

Added simple line-splitting to ``run_script()``.

1.2
---

Modified ``run_script()`` so that if *ignore_error* is False any
exception caused by the external application is re-raised.  This
"breaks" a build if there is a problem generating the cog output in an
rst file, and makes it easier to spot problems with the cog
instructions.

1.1
---

Updated to include ``run_script()`` function.

1.0
---

First public release based on the versions of these functions
developed for PyMOTW_.
