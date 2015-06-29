Frequently-asked questions
==========================

 -  Is there, or will there be, support for :mod:`optparse`?

    Because :mod:`optparse` was deprecated in Python 2.7, we have no plans
    to support it at present. If you'd still like to use :obj:`argdoc`,
    see the Python documentation on
    `upgrading optparse code <http://docs.python.org/2.7/library/argparse.html#upgrading-optparse-codeimport warnings>`_.

 -  My :term:`main-like function` is not named `main`. Can I use :obj:`argdoc`
    without changing the function name?

    Absolutely. Just set ``argdoc_main_func`` to the name of your function
    (as a string) in ``conf.py``. See :doc:`advanced` for instructions.
