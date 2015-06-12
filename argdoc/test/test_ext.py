#!/usr/bin/env python
"""Test suite for :obj:`argdoc.ext`

Argument-matching atterns in :mod:`argdoc.ext` are tested with a battery
of unit tests.

The docstring processing machinery is tested via a call to `sphinx-build`
on executable scripts included as part of the test dataset. The output
HTML files are compared against expectation. Admittedly, this is a fragile
test.
"""
__date__   = "2015-06-09"
__author__ = "Joshua Griffin Dunn"

import argparse
import os
import tempfile
import shlex
import shutil
from pkg_resources import resource_filename, cleanup_resources
from nose.tools import assert_equal, assert_true
from nose.plugins.attrib import attr
from sphinx import main as sphinxbuild
from argdoc.ext import patterns


class TestArgdoc():
    """Test case for functions defined in :mod:`argdoc.ext`"""

    @classmethod
    def setUpClass(cls):
        # retain record indicating whether builder has been run,
        # so we run it a maximum of once, and only if we decide to do 
        # the expensive tests
        cls.built = False

        # options for sphinx-build runs
        cls.optdict = { "sourcedir" : resource_filename("argdoc","test/testdocroot"),
                          "conf"     : resource_filename("argdoc","test/testdocroot/conf.py"),
                          "outdir"   : tempfile.mkdtemp(prefix="argdoc"),
                       }

        cls.sphinxopts = "-Q -b html %(sourcedir)s %(outdir)s" % cls.optdict

        # test cases for patterns
        cls.pattern_tests = {}
        cls.pattern_tests["section_title"] = [("optional arguments:", ("optional arguments",)),
                                           ("optional arguments: ",None),
                                           (" optional arguments:",None),
                                           ("optional: arguments:",("optional: arguments",)),
                                           ("positional arguments:",("positional arguments",)),
                                           ("some long string (with parentheses):",("some long string (with parentheses)",)),
                                           ]
        cls.pattern_tests["opt_only"] = [
                                      ("  positional1",('positional1',None)),
                                      ("  po3413134",('po3413134',None)),
                                      ("  reallyreallyreallyreallyreallyreallyreallyreallylongpositional",("reallyreallyreallyreallyreallyreallyreallyreallylongpositional",None)),
                                      ("  --help",    ('--help', None)),
                                      ("  -h",        ('-h', None)),
                                      ("  -h, --help",('-h', '--help')),
                                      # opt + args + desc
                                      ("  -n M, --ne M            some description", None),
                                      ("  -n M M, --ne M M        some description", None),
                                      ("  -n M M M, --ne M M M    some description", None),
                                      ("  -n M                    some description", None),
                                      ("  -n M M                  some description", None),
                                      ("  -n M M M                some description", None),
                                      ("  --ne M                  some description", None),
                                      ("  --ne M M                some description", None),
                                      ("  --ne M M M              some description", None),
                                      # opt + desc
                                      ("  -n, --ne                some description", None),
                                      ("  -n                      some description", None),
                                      ("  --ne                    some description", None),
                                      # opt + args
                                      ("-n M, --ne M", None),
                                      ("-n M M, --ne M M", None),
                                      ("-n M M M, --ne M M M", None),
                                      ("-n M", None),
                                      ("-n M M", None),
                                      ("-n M M M", None),
                                      ("--ne M", None),
                                      ("--ne M M", None),
                                      ("--ne M M M", None),
                                      ]
        cls.pattern_tests["opt_plus_args"] = [("  -o FILENAME, --out FILENAME",('-o', ' FILENAME', '--out', ' FILENAME')),
                                           ("  -o FILENAME",('-o', ' FILENAME', None, None)),
                                           ("  --out FILENAME",('--out', ' FILENAME', None, None)),
                                           ("-o FILENAME, --out FILENAME",None),
                                           ("-o FILENAME",None),
                                           ("--out FILENAME",None),                               
                                           ("  -n M M, --num M M",('-n', ' M M', '--num', ' M M')),
                                           ("  -n M M",('-n', ' M M', None,None)),
                                           ("  --num M M",('--num', ' M M',None,None)),
                                           ("-n M M, --num M M",None),
                                           ("-n M M",None),
                                           ("--num M M",None),
                                           # opt + args + desc
                                           ("  -n M, --ne M            some description", None),
                                           ("  -n M M, --ne M M        some description", None),
                                           ("  -n M M M, --ne M M M    some description", None),
                                           ("  -n M                    some description", None),
                                           ("  -n M M                  some description", None),
                                           ("  -n M M M                some description", None),
                                           ("  --ne M                  some description", None),
                                           ("  --ne M M                some description", None),
                                           ("  --ne M M M              some description", None),
                                           # opt + desc
                                           ("  -n, --ne                some description", None),
                                           ("  -n                      some description", None),
                                           ("  --ne                    some description", None),
                                           # opt only
                                           ("  --help", None),    
                                           ("  -h",     None),
                                           ("  -h, --help", None),
                                            ]
        cls.pattern_tests["opt_plus_desc"] = [("  -h, --help            show this help message and exit",('-h, --help', ', --help', 'show this help message and exit')),
                                           ("  -h                    show this help message and exit",('-h',None, 'show this help message and exit')),
                                           ("  --help                show this help message and exit",('--help',None, 'show this help message and exit')),
                                           ("  -h, --help     show this help message and exit",('-h, --help', ', --help', 'show this help message and exit')),
                                           ("  -h             show this help message and exit",('-h',None, 'show this help message and exit')),
                                           ("  --help         show this help message and exit",('--help',None, 'show this help message and exit')),
                                           ("-h, --help     show this help message and exit",None),
                                           ("-h             show this help message and exit",None),
                                           ("--help         show this help message and exit",None),
                                           # opt only
                                           ("  --help",    None),
                                           ("  -h",        None),
                                           ("  -h, --help",None),
                                           # opt + args + desc
                                           ("  -n M, --ne M            some description", None),
                                           ("  -n M M, --ne M M        some description", None),
                                           ("  -n M M M, --ne M M M    some description", None),
                                           ("  -n M                    some description", None),
                                           ("  -n M M                  some description", None),
                                           ("  -n M M M                some description", None),
                                           ("  --ne M                  some description", None),
                                           ("  --ne M M                some description", None),
                                           ("  --ne M M M              some description", None),
                                           # opt + args
                                           ("-n M, --ne M", None),
                                           ("-n M M, --ne M M", None),
                                           ("-n M M M, --ne M M M", None),
                                           ("-n M", None),
                                           ("-n M M", None),
                                           ("-n M M M", None),
                                           ("--ne M", None),
                                           ("--ne M M", None),
                                           ("--ne M M M", None),
                                           ]
        cls.pattern_tests["opt_plus_args_desc"] = [
             ("  -n M, --ne M            some description", {"left" : "-n M, --ne M",         "right" : "some description"}),
             ("  -n M M, --ne M M        some description", {"left" : "-n M M, --ne M M",     "right" : "some description"}),
             ("  -n M M M, --ne M M M    some description", {"left" : "-n M M M, --ne M M M", "right" : "some description"}),
             ("  -n M                    some description", {"left" : "-n M",       "right" : "some description"}),
             ("  -n M M                  some description", {"left" : "-n M M",     "right" : "some description"}),
             ("  -n M M M                some description", {"left" : "-n M M M",   "right" : "some description"}),
             ("  --ne M                  some description", {"left" : "--ne M",     "right" : "some description"}),
             ("  --ne M M                some description", {"left" : "--ne M M",   "right" : "some description"}),
             ("  --ne M M M              some description", {"left" : "--ne M M M", "right" : "some description"}),
             # opt + args
             ("  -n M, --ne M            ", None),
             ("  -n M M, --ne M M        ", None),
             ("  -n M M M, --ne M M M    ", None),
             ("  -n M                    ", None),
             ("  -n M M                  ", None),
             ("  -n M M M                ", None),
             ("  --ne M                  ", None),
             ("  --ne M M                ", None),
             ("  --ne M M M              ", None),
             # opt + desc
             ("  -n , --ne             some description", None),
             ("  -n  , --ne          some description", None),
             ("  -n   , --ne       some description", None),
             ("  -n                     some description", None),
             ("  -n                    some description", None),
             ("  -n                   some description", None),
             ("  --ne                   some description", None),
             ("  --ne                  some description", None),
             ("  --ne                 some description", None),
             # opt only
             ("  --help", None),    
             ("  -h",     None),
             ("  -h, --help", None),
                                                ]
        cls.pattern_tests["subcommand_names"] = {("  {one,another,four,five}",("one,another,four,five",)),
                                              ("  {one,another,four}",("one,another,four",)),
                                              ("  {one,another}",("one,another",)),
                                              ("  {just_one}",("just_one",)),
                                              ("{one,another,four,five}",None),
                                              ("{one,another,four}",None),
                                              ("{one,another}",None),
                                              ("{just_one}",None),                                              
                                              }
        cls.pattern_tests["continue_desc"] = []
        cls.pattern_tests["section_desc"] = []

    @classmethod
    def tearDownClass(cls):
        """Clean up temp files after tests are complete"""
        cleanup_resources()
        shutil.rmtree(cls.optdict["outdir"])

    @classmethod
    def run_builder(cls):
        """Run sphinx builder the first time it is called, only

        Raises
        ------
        AssertionError
            If builder exists with non-zero status
        """
        if cls.built == False:
            try:
                sphinxbuild(shlex.split(cls.sphinxopts))
            except SystemExit as e:
                if e.code != 0:
                    raise AssertionError("Error running sphinx-build (exited with code %s)" % e.code)

            cls.built = True

    @staticmethod
    def check_match(test_name,pat,inp,expected):
        """Check patterns for matching, or non-matching

        Parameters
        ----------
        test_name : str
            Name of test set being executed

        pat : :class:`re.compile`
            Pattern to test

        inp : str
            Input to test

        expected : dict, tuple, or None
            Expected result. If a `dict`, equivalence is tested with
            `pat.match(inp).groupdict()` is called to test equivalence.
            If a 'tuple' equivalence is tested with `pat.match(inp).groups()`,
            :meth:`re.compile.groups` is called. If `None`, it is asserted
            that `pat.match(inp)` is `None` 
        """
        if expected is None:
            msg = "For test '%s', pattern %s' matched '%s', " % (test_name,
                                                                 pat.pattern,
                                                                 inp)
            assert_true(pat.match(inp) is None,msg)
        else:
            if isinstance(expected,dict):
                groups = pat.match(inp).groupdict()
            else:
                groups = pat.match(inp).groups()
            msg = "For test '%s', pattern %s' input '%s': expected %s, got %s " % (test_name,
                                                                                   pat.pattern,
                                                                                   inp,
                                                                                   expected,
                                                                                   groups)
            assert_equal(expected,groups,msg)
    
    def test_patterns(self):
        for name, cases in self.pattern_tests.items():
            for inp,expected in cases:
                yield self.check_match, name, patterns[name], inp, expected

    @attr(kind="functional")
    def test_simple_parser(self):
        self.run_builder()
        assert False

    @attr(kind="functional")
    def test_optiongroup_parser(self):
        self.run_builder()
        assert False

    @attr(kind="functional")
    def test_with_subparsers(self):
        self.run_builder()
        assert False

    def test_process_argparser_help(self):
        assert False
     
