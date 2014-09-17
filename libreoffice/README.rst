.. -*- restructuredtext -*-

================================
LibreOffice extension for Sphinx
================================

:author: Gerard Marull-Paretas <gerardmarull@gmail.com>


About
=====

This extensions allows to render any supported LibreOffice drawing format 
(e.g. odg, vsd...) 


Quick Example
-------------

A simple example::

    .. libreoffice:: /path/to/drawing.odg
       :align: center
       :autocrop:

       The optional caption



Requirements
------------

* LibreOffice_
* Pillow_

.. warning::
    LibreOffice 4.3 is known to **NOT** work. Use other versions instead.


Enabling the extension in Sphinx_
---------------------------------

Just add ``sphinxcontrib.libreoffice`` to the list of extensions in the 
``conf.py`` file. For example::

    extensions = ['sphinxcontrib.libreoffice']


Usage
=====

Options
-------

``autocrop``
  Remove empty margins from the rendered drawings (image formats only)

All options from ``figure`` directive can be used (e.g. scale, target...)

Configuration
-------------

Two optional configurations are added to Sphinx_. They can be set in
``conf.py`` file:

``libreoffice_fromat`` <dict>:
  image format used for the different builders. ``latex`` and ``html`` fromats
  are supported.

  For example::

    libreoffice_format = dict(latex='pdf', html='png')

  These are the actual defaults.

``libreoffice_binary`` <str>:
  path to the LibreOffice binary (soffice). LibreOffice binary path will be 
  automatically determined by the extension. Use only if you need to indicate a 
  specific version or you have it installed in a custom path.

.. Links:
.. _libreoffice: http://www.libreoffice.org/
.. _Pillow: https://pypi.python.org/pypi/Pillow
.. _Sphinx: http://sphinx-doc.org/

