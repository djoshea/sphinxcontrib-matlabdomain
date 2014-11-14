autoanysrc
==========

.. attention::

    Currently in early development stage

Extension for gathering reST documentation from any files.
This is a documenter_ from ext.autodoc.

In current state this extension will only insert reST docs from files to
target documentation project without auto generation definitions
and signatures.

But it simple and clean to make documentation for API and store documentation
strings in the source code.

Install
-------

::

    pip install sphinxcontrib-autoanysrc


Usage
-----

Add autoanysrc to extensions list::

    extensions = ['sphinx.ext.autodoc', 'sphinxcontrib.autoanysrc', ]

Example of usage::

    .. autoanysrc:: directives
        :src: app/**/*.js
        :analyzer: js

.. note::

    directive argument not used now, but it required...

Where:

 - `src` option is the pattern to list source files where docs are stored
 - `analyzer` option to determine witch analyzer must be used for
   processing this files

Directive will iterate over `app/**/*.js` files and process
it line by line.


JSAnalyzer
----------

Search comments blocks starts by `/*"""` and ends by `*/`
(inspired by `Nuulogic/sphinx-jsapidoc`_).


For example services.js::

    /*"""
    Services
    ````````

    The function :func:`someService` does a some function.
    */

    function someService(href, callback, errback) {
    /*"""
    .. function:: someService(href, callback[, errback])

        :param string href: An URI to the location of the resource.
        :param callback: Gets called with the object.
        :throws SomeError: For whatever reason in that case.
        :returns: Something.
    */
        return 'some result';
    };



TODO
----

- encoding option
- allow internal indent in comment block
- registering custom analyzers from settings
- generate signatures like ext.autodoc...


.. _documenter: http://sphinx-doc.org/extdev/appapi.html?highlight=documenter#sphinx.application.Sphinx.add_autodocumenter
.. _`Nuulogic/sphinx-jsapidoc`: https://github.com/Nuulogic/sphinx-jsapidoc
