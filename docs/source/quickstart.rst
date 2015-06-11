Quickstart
==========

Installation
------------
Install stable versions via via :obj:`pip`. For a single-user installation::

    $ pip install --user argdoc


For a system-wide installation::

    $ sudo pip install argdoc


Setting up :obj:`argdoc`
-----------------------
Setting up :obj:`argdoc` only takes a few steps:

 1. Find the `extensions` definition in your `Sphinx`_ configuration file,
    ``conf.py``, and add `'argdoc.ext'` to the list. For example::

        # inside conf.py
        extensions = [
            'sphinx.ext.autodoc',
            'sphinx.ext.autosummary',
            'sphinx.ext.intersphinx',
            'argdoc.ext' # <---- ta-da!
        ]

 2. Generate document stubs for your package. It is easiest to use
    `sphinx-apidoc`_::
     
        $ cd my_project_folder/my_package_folder
        $ sphinx-apidoc -e -o docs/source/generated my_package_name
  
    Or you can make your document stubs manually. Just make sure the
    stubs for your command-line scripts final document includes the
    ``.. automodule :`` `directive`_. For example::

         .. automodule:: crossgen.crossgen
            :members:
            :undoc-members:
            :show-inheritance:

 3. Make sure your command-line script uses :class:`argparse.ArgumentParser`
    to parse its arguments, and defines a :term:`main-like function` that
    is called when the script is executed from the command line.
    
    If you want your documentation to be extra nice, write a user-friendly
    description of your script in its :term:`module docstring`, and pass
    the docstring contents as a `description` to your
    :class:`~argparse.ArgumentParser`. For example::

        #!/usr/bin/env python
        """This is my module docstring, which describes what my script does
        at length, so that users can figure out what it does. Conveniently
        this text is used both by argparse as command-line help text, and
        by Sphinx when generating HTML documentation.
        """
        import argparse

        # other functions et c here
        ...

        def main():
            """This is the body of the program"""
            my_parser = argparse.ArgumentParser(description=__doc__,
                                                formatter_class=argparse.RawDescriptionHelpFormatter)
            my_parser.add_argument("some_arg",type=str,help="some helptext, if you want")
            my_parser.add_argument("--some_keyword",type=int,help="Some other helptext")
            # et c. other options & program body

            args = argparse.parse_args()

            # rest of main()
            ...

        if __name__ == "__main__":
            main()


    That's it! There is nothing else you need to do. For further info
    or configuration options, see :doc:`advanced`.
