# -*- coding: utf-8 -*-
"""Setup file for argdoc Sphinx extension"""
from setuptools import setup, find_packages
import sphinxcontrib.argdoc

with open("README.rst") as f:
    long_description = f.read()

config_info = { "version"          : sphinxcontrib.argdoc.__version__,
                "packages"         : find_packages(),
                "long_description" : long_description,
              }

setup(
    name = "sphinxcontrib-argdoc",
    description = 'Sphinx "argdoc" extension',
    #description  = "Sphinx extension that automatically adds tables describing command-line arguments to autodoc's `:automodule:` directive",
    url          = "http://bitbucket.org/birkenfeld/sphinx-contrib",
    download_url = "http://pypi.python.org/pypi/sphinxcontrib-argdoc",

    author           = "Joshua Griffin Dunn",
    author_email     = "joshua.g.dunn@gmail.com",
    maintainer       = "Joshua Griffin Dunn",
    maintainer_email = "Joshua Griffin Dunn",
    
    license   = "BSD 3-Clause",
    keywords  = "sphinx documentation argparse command-line autodoc",
    platforms = "any", 

    zip_safe = True,

    install_requires = [
                "sphinx>=1.3.1",
                "autodoc>=0.3",
                ],
    
    tests_require=["nose>=1.0"],
    test_suite = "nose.collector",
    namespace_packages=['sphinxcontrib'],
    
    classifiers=[
         'Development Status :: 4 - Beta',
         'Environment :: Plugins',
         'Environment :: Web Environment',
         'Programming Language :: Python',
         'Programming Language :: Python :: 2.7',
         'Programming Language :: Python :: 3',

         'Framework :: Sphinx :: Extension'

         'Topic :: Documentation',
         'Topic :: Documentation :: Sphinx',
         'Topic :: Software Development :: Documentation',
         'Topic :: Text Processing',
         'Topic :: Utilities',

         'Intended Audience :: Developers',
         'License :: OSI Approved :: BSD License',
         'Natural Language :: English',
         'Operating System :: OS Independent',
        ],
    **config_info
)
