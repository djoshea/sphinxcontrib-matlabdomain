Advanced usage
==============

Skipping a :term:`main-like function`
-------------------------------------
To prevent :obj:`argdoc` from processing a :term:`main-like function`,
use the :func:`~argdoc.ext.noargdoc` function decorator. For example::

    #!/usr/bin/env python
    import argparse
    from argdoc.ext import noargdoc

    @noargdoc
    def main():
        """Main-like function that would normally be processed by `argdoc`,
        but that we are skipping instead!
        """
        # main function body here
        parser = argparse.ArgumentParser()
        pass

    if __name__ == "__main__":
        main()


Processing a :term:`main-like function` that is not named `main`
----------------------------------------------------------------
If your code conventions use a name different from `main` for
:term:`main-like functions <main-like function>`, :obj:`argdoc`
can still process these. Just set the value of the configuration
parameter ``argdoc_main_func`` to your function name in ``conf.py``::

    ...

    # somewhere in conf.py
    argdoc_main_func = "whatever_we_call_main_funcs_at_our_organization"

    ...
