Glossary of terms
=================

 .. glossary ::
    :sorted:

    command line
    command-line
        A text-based prompt from which commands can be executed, for
        example, in a terminal session.

    shell
        An environment that executes commands. This could be a
        :term:`command-line` environment like the `bash`_ prompt, or
        a graphical environment like the OSX Finder.

    main-like function
        A function that is called when a script is executed from a
        :term:`shell`, as opposed to inside an interactive Python session.
        These are the functions from whose arguments :obj:`argdoc` generates
        documentation.
        
        These are typically named `main`, and in idiomatically written
        Python are called by the following lines, which appear as the 
        final lines of executable scripts::

            if __name__ == "__main__":
                main()

        which are used because Python only sets the `__name__` attribute
        to `__main__` if a script is executed from a :term:`shell`.

        :obj:`argdoc` detects :term:`main-like functions <main-like function>`
        by scanning modules for functions named whatever the current
        value of `argdoc_main_func` is set to in your `Sphinx`_
        configuration file ``conf.py``. By default, the value of
        `argdoc_main_func` is `main`.
