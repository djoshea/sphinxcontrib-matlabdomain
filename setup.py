#!/usr/bin/env python
"""Setup file for argdoc Sphinx extension"""
from setuptools import setup, find_packages
import argdoc

with open("README.md") as f:
    long_description = f.read()


config_info = { "version"      : argdoc.__version__,
                "packages"     : find_packages(),
              }

setup(
    name = "argdoc",
    url          = "",
    download_url = "",

    install_requires = [
    	                "sphinx>=1.3.1",
                        "autodoc>=0.3",
                        ],

    zip_safe = True,

    # metadata for upload to PyPI
    author           = "Joshua Griffin Dunn",
    author_email     = "joshua.g.dunn@gmail.com",
    maintainer       = "Joshua Griffin Dunn",
    maintainer_email = "Joshua Griffin Dunn",
    
    description = "Sphinx extension that automatically adds tables describing command-line arguments to autodoc's `:automodule:` directive",
    long_description = long_description,
    license   = "BSD 3-Clause",
    keywords  = "sphinx documentation argparse command-line autodoc",
    platforms = "any", 
    
    tests_require=["nose>=1.0"],
    test_suite = "nose.collector",
    
    classifiers=[
         'Programming Language :: Python',
         'Programming Language :: Python :: 2.7',
         'Programming Language :: Python :: 3',

         'Framework :: Sphinx :: Extension'

         'Topic :: Documentation',
         'Topic :: Documentation :: Sphinx',
         'Topic :: Text Processing',
         'Topic :: Utilities',

         'Intended Audience :: Developers',
         'License :: BSD 3-Clause',
         
         'Operating System :: POSIX',
         'Operating System :: MacOS :: MacOS X',
         'Operating System :: Microsoft :: Windows',
        ],
    **config_info
)
