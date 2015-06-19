# welcome to `argdoc`

## Introduction

`argdoc` is an extension for the [Sphinx](https://sphinx-doc.org)
documentation engine.

It automatically generates tables describing command-line arguments
for executable scripts written in Python, and inserts those tables
into the `:automodule:` documentation generated for the scripts by
the Sphinx extension [autodoc](http://sphinx-doc.org/ext/autodoc.html).

The only requirements are:

  1. The executable scripts use the Python
     [argparse](https://docs.python.org/3/library/argparse.html) module
     for argument parsing.

  2. The `rst` documentation stub file for the scripts include
     the `:automodule:` directive (which they will, by default,
     if you use `sphinx-apidoc`).

For more info, detailed instructions, and examples, see the
[argdoc documentation]().


## Installation and use

`argdoc` may be installed from [PyPI](https://pypi.python.org)
using [pip](https://pip.pypa.io/en/latest/installing.html). Alternatively,
you can clone the development version into your PYTHONPATH.

To use `argdoc`, simply add `'argdoc.ext'` to the list of extensions
in your project's Sphinx configuration file,
[conf.py](http://sphinx-doc.org/config.html)


## Tests
Tests are written using [nose](https://nose.readthedocs.org),
and may be found in the subpackage `argdoc.test`. To run the tests,
type from the terminal:

    `$ nosetests argdoc.test`


## Authors
  - [Joshua Griffin Dunn]()


## License
`argdoc` is licensed under the
[BSD 3-Clause License](http://opensource.org/licenses/BSD-3-Clause).
