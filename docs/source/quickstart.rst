Quickstart
==========

Installation
------------
Install stable versions via `pip`_. For a single-user installation:

 .. code-block:: shell

    $ pip install --user argdoc


For a system-wide installation:

 .. code-block:: shell

    $ sudo pip install argdoc


Setting up :obj:`argdoc`
------------------------
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
    `sphinx-apidoc`_:
     
     .. code-block:: shell

        $ cd my_project_folder/my_package_folder
        $ sphinx-apidoc -e -o docs/source/generated my_package_name
  
    Or you can make your document stubs manually. Just make sure the
    final document stubs for your :term:`executable scripts` include the
    ``.. automodule :`` `directive`_. For example:

     .. code-block:: rest

         .. automodule:: some_package.some_module
            :members:
            :undoc-members:
            :show-inheritance:

 3. Make sure your :term:`executable scripts` use :class:`argparse.ArgumentParser`
    to parse their arguments, and define a :term:`main-like function` that
    is called when the script is executed from the :term:`shell`.
    
    If you want your documentation to be extra nice, write a user-friendly
    description of your script in its :term:`module docstring`, and pass
    the docstring contents as a `description` to your
    :class:`~argparse.ArgumentParser`. For example::

        #!/usr/bin/env python
        """This is my module docstring, which describes what my script does
        at length, so that users can figure out what it does. Conveniently
        this text is used both by argparse as help text in the shell, and
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
    or configuration options, see :doc:`advanced`. For examples, see
    :doc:`examples`.

 .. warning::
    :obj:`argdoc` generates its documentation by calling your executable
    scripts with the argument ``--help``. Therefore, any side effects
    caused by executing your script will take effect during the documentation
    build process.
