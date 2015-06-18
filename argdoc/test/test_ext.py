#!/usr/bin/env python
# coding: utf-8
"""Test suite for :obj:`argdoc.ext`

"""
__date__   = "2015-06-09"
__author__ = "Joshua Griffin Dunn"

import os
import tempfile
import shlex
import shutil
import cStringIO
import importlib
import argdoc.test.cases
import sys


from modulefinder import ModuleFinder
from pkg_resources import resource_filename, cleanup_resources
from nose.tools import assert_equal, assert_true, assert_dict_equal
from nose.plugins.attrib import attr
from sphinx import main as sphinxbuild
from argdoc.ext import get_patterns, get_col1_text, get_col2_text, noargdoc,\
                       post_process_automodule,\
                       format_argparser_to_docstring




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
                        "conf"      : resource_filename("argdoc","test/testdocroot/conf.py"),
                        "outdir"    : tempfile.mkdtemp(prefix="argdoc"),
                       }

        cls.sphinxopts = "-Q -b html %(sourcedir)s %(outdir)s" % cls.optdict

        # test cases for patterns
        cls.pattern_tests = {}
        cls.pattern_tests["positional_arg"] = [("  arg1",{"arg1":"arg1","desc":None}),
                                               ("  some_arg         some_description with lots of words",
                                                { "arg1" : "some_arg",
                                                  "desc" : "some_description with lots of words"
                                                }
                                               ),
                                               ("optional arguments:",None),
                                               ("  --kwarg M",None),
                                               ("  -k M",None),
                                               ("  -k",None),
                                               ("  --kwarg",None),
                                               ("  -k, --kwarg",None),
                                               ("  -k M, --kwarg M",None),
                                               ("  -k             some_description with lots of words",None),
                                               ("  --kwarg        some_description with lots of words",None),
                                               ("  -k, --kwarg    some_description with lots of words",None),
                                               ("  -k M           some_description with lots of words",None),
                                               ("  --kwarg M      some_description with lots of words",None),
                                               ("  -k M, --kwarg M   some_description with lots of words",None),
                ]
        cls.pattern_tests["section_title"] = [("optional arguments:", ("optional arguments",)),
                                           ("optional arguments: ",None),
                                           (" optional arguments:",None),
                                           ("optional: arguments:",("optional: arguments",)),
                                           ("positional arguments:",("positional arguments",)),
                                           ("some long string (with parentheses):",("some long string (with parentheses)",)),
                                           ]
        cls.pattern_tests["arg_only"] = [
                                      ("  positional1",('positional1',None)),
                                      ("  po3413134",('po3413134',None)),
                                      ("  reallyreallyreallyreallyreallyreallyreallyreallylongpositional",("reallyreallyreallyreallyreallyreallyreallyreallylongpositional",None)),
                                      ("  --help",    ('--help', None)),
                                      ("  -h",        ('-h', None)),
                                      ("  -h, --help",('-h', '--help')),
                                      # arg + valss + desc
                                      ("  -n M, --ne M            some description", None),
                                      ("  -n M M, --ne M M        some description", None),
                                      ("  -n M M M, --ne M M M    some description", None),
                                      ("  -n M                    some description", None),
                                      ("  -n M M                  some description", None),
                                      ("  -n M M M                some description", None),
                                      ("  --ne M                  some description", None),
                                      ("  --ne M M                some description", None),
                                      ("  --ne M M M              some description", None),
                                      # arg + desc
                                      ("  -n, --ne                some description", None),
                                      ("  -n                      some description", None),
                                      ("  --ne                    some description", None),
                                      # arg + vals
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
        cls.pattern_tests["arg_plus_val"] = [("  -o FILENAME, --out FILENAME",('-o', ' FILENAME', '--out', ' FILENAME')),
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
                                           # arg + vals + desc
                                           ("  -n M, --ne M            some description", None),
                                           ("  -n M M, --ne M M        some description", None),
                                           ("  -n M M M, --ne M M M    some description", None),
                                           ("  -n M                    some description", None),
                                           ("  -n M M                  some description", None),
                                           ("  -n M M M                some description", None),
                                           ("  --ne M                  some description", None),
                                           ("  --ne M M                some description", None),
                                           ("  --ne M M M              some description", None),
                                           # arg + desc
                                           ("  -n, --ne                some description", None),
                                           ("  -n                      some description", None),
                                           ("  --ne                    some description", None),
                                           # arg only
                                           ("  --help", None),    
                                           ("  -h",     None),
                                           ("  -h, --help", None),
                                            ]
        cls.pattern_tests["arg_plus_desc"] = [("  -h, --help            show this help message and exit",('-h','--help','show this help message and exit')),
                                           ("  -h                    show this help message and exit",('-h',None, 'show this help message and exit')),
                                           ("  --help                show this help message and exit",('--help',None, 'show this help message and exit')),
                                           ("  -h, --help     show this help message and exit",('-h','--help','show this help message and exit')),
                                           ("  -h             show this help message and exit",('-h',None, 'show this help message and exit')),
                                           ("  --help         show this help message and exit",('--help',None, 'show this help message and exit')),
                                           ("-h, --help     show this help message and exit",None),
                                           ("-h             show this help message and exit",None),
                                           ("--help         show this help message and exit",None),
                                           # arg only
                                           ("  --help",    None),
                                           ("  -h",        None),
                                           ("  -h, --help",None),
                                           # arg + vals + desc
                                           ("  -n M, --ne M            some description", None),
                                           ("  -n M M, --ne M M        some description", None),
                                           ("  -n M M M, --ne M M M    some description", None),
                                           ("  -n M                    some description", None),
                                           ("  -n M M                  some description", None),
                                           ("  -n M M M                some description", None),
                                           ("  --ne M                  some description", None),
                                           ("  --ne M M                some description", None),
                                           ("  --ne M M M              some description", None),
                                           # arg + vals
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
        cls.pattern_tests["arg_plus_val_desc"] = [
             ("  -n M, --ne M            some description", {"arg1" : "-n", "val1" : " M",    "arg2" : "--ne", "val2" : " M",     "desc" : "some description"}),
             ("  -n M M, --ne M M        some description", {"arg1" : "-n", "val1" : " M M",  "arg2" : "--ne", "val2" : " M M",   "desc" : "some description"}),
             ("  -n M M M, --ne M M M    some description", {"arg1" : "-n", "val1" : " M M M","arg2" : "--ne", "val2" : " M M M", "desc" : "some description"}),
             ("  -n M                    some description", {"arg1" : "-n", "val1" : " M",    "arg2" : None,   "val2" : None,     "desc" : "some description"}),
             ("  -n M M                  some description", {"arg1" : "-n", "val1" : " M M",  "arg2" : None,   "val2" : None,     "desc" : "some description"}),
             ("  -n M M M                some description", {"arg1" : "-n", "val1" : " M M M","arg2" : None,   "val2" : None,     "desc" : "some description"}),
             ("  --ne M                  some description", {"arg1" : "--ne", "val1" : " M",     "arg2" : None,   "val2" : None, "desc" : "some description"}),
             ("  --ne M M                some description", {"arg1" : "--ne", "val1" : " M M",   "arg2" : None,   "val2" : None, "desc" : "some description"}),
             ("  --ne M M M              some description", {"arg1" : "--ne", "val1" : " M M M", "arg2" : None,   "val2" : None, "desc" : "some description"}),
             # arg + vals
             ("  -n M, --ne M            ", None),
             ("  -n M M, --ne M M        ", None),
             ("  -n M M M, --ne M M M    ", None),
             ("  -n M                    ", None),
             ("  -n M M                  ", None),
             ("  -n M M M                ", None),
             ("  --ne M                  ", None),
             ("  --ne M M                ", None),
             ("  --ne M M M              ", None),
             # arg only
             ("  --help", None),    
             ("  -h",     None),
             ("  -h, --help", None),
             # arg + desc
             ("  -n, --ne                some description", None),
             ("  -n                      some description", None),
             ("  --ne                    some description", None),
             # positional
             ("  positional1",None),
             ("  po3413134",None),
             ("  reallyreallyreallyreallyreallyreallyreallyreallylongpositional",None),
                          
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
        cls.pattern_tests["section_desc"] = [
            ("  choose one of the following:",("choose one of the following:",)),
            ("  Sometimes it is useful to group arguments that relate to each other in an",
             ("Sometimes it is useful to group arguments that relate to each other in an",)),
            ("  Description of second argument group",("Description of second argument group",)),
            ("  A special group of arguments in the `bar` subparser",("A special group of arguments in the `bar` subparser",)),
            ("  Oneworddescription",None),

             # arg + vals
             ("  -n M, --ne M            ", None),
             ("  -n M M, --ne M M        ", None),
             ("  -n M M M, --ne M M M    ", None),
             ("  -n M                    ", None),
             ("  -n M M                  ", None),
             ("  -n M M M                ", None),
             ("  --ne M                  ", None),
             ("  --ne M M                ", None),
             ("  --ne M M M              ", None),
             # arg + vals + desc
             ("  -n , --ne             some description", None),
             ("  -n  , --ne          some description", None),
             ("  -n   , --ne       some description", None),
             ("  -n                     some description", None),
             ("  -n                    some description", None),
             ("  -n                   some description", None),
             ("  --ne                   some description", None),
             ("  --ne                  some description", None),
             ("  --ne                 some description", None),
             # arg only
             ("  --help", None),    
             ("  -h",     None),
             ("  -h, --help", None),
             ("  arg1",None),
             ("  some_arg         some_description with lots of words",None),
        ]

        # test cases for test_get_col1_text, test_get_col2_text
        cls.match_dicts = [
                { "arg1" : "ARG",
                  "col1" : "``ARG``",
                  "col2" : "",
                },
                { "arg1" : "ARG",
                  "desc" : "some description",
                  "col1" : "``ARG``",
                  "col2" : "some description",
                },
                { "arg1" : "-v",
                  "val1" : "ARG",
                  "col1" : "``-v ARG``",
                  "col2" : "",
                },
                { "arg1" : "--val",
                  "val1" : "ARG",
                  "col1" : "``--val ARG``",
                  "col2" : ""
                },
                { "arg1" : "-v",
                  "val1" : "ARG",
                  "arg2" : "--val",
                  "val2" : "ARG",
                  "desc" : "some description",
                  "col1" : "``-v ARG``, ``--val ARG``",
                  "col2" : "some description",
                },
                { "arg1" : "-v",
                  "val1" : "ARG",
                  "desc" : "some description",
                  "col1" : "``-v ARG``",
                  "col2" : "some description",
                },
                { "arg1" : "--val",
                  "val1" : "ARG",
                  "desc" : "some description",
                  "col1" : "``--val ARG``",
                  "col2" : "some description",
                },
                { "arg1" : "-v",
                  "val1" : "ARG",
                  "arg2" : "--val",
                  "val2" : "ARG",
                  "desc" : "some description",
                  "col1" : "``-v ARG``, ``--val ARG``",
                  "col2" : "some description",
                },
                { "arg1" : "-v",
                  "arg2" : "--val",
                  "col1" : "``-v``, ``--val``",
                  "col2" : ""
                },
                { "arg1" : "-v",
                  "arg2" : "--val",
                  "desc" : "some description",
                  "col1" : "``-v``, ``--val``",
                  "col2" : "some description",
                },

                ]

        # automatically load module test cases for functional tests
        # testcase names mapped to (module, expected rst output, built rst output)
        cls.test_cases = {}
        mf = ModuleFinder()
        for modname in mf.find_all_submodules(argdoc.test.cases):
            if modname not in (__name__,"__init__"):
                mod = importlib.import_module("argdoc.test.cases.%s" % modname)
                basename = "argdoc.test.cases.%s_docstring.rst" % modname
                tup = (mod,
                       resource_filename("argdoc","test/testbuild/%s" % basename),
                       os.path.join(cls.optdict["outdir"],basename))
                cls.test_cases[modname] = tup
 
    @classmethod
    def tearDownClass(cls):
        """Clean up temp files after tests are complete"""
        cleanup_resources()
        shutil.rmtree(cls.optdict["outdir"])

    @classmethod
    def run_builder(cls):
        """Run sphinx builder only the first time it is needed

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
    def check_pattern(test_name,pat,inp,expected):
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
                fn = assert_dict_equal
            else:
                groups = pat.match(inp).groups()
                fn = assert_equal
            msg = "For test '%s', pattern %s' input '%s': expected %s, got %s " % (test_name,
                                                                                   pat.pattern,
                                                                                   inp,
                                                                                   expected,
                                                                                   groups)
            fn(expected,groups,msg)
    
    def test_patterns(self):
        # test all patterns
        patterns = get_patterns("-")
        for name, cases in self.pattern_tests.items():
            for inp,expected in cases:
                yield self.check_pattern, name, patterns[name], inp, expected

    @staticmethod
    def check_equal(expected,found,casename=""):
        """Helper method just to allow us to use test generators in other tests"""
        if isinstance(expected,list):
            idx = 2
        elif isinstance(expected,str):
            idx = 80
        else:
            idx = None

        ellip = "..." if len(expected) > idx else ""

        message = "Expected '%s%s', found '%s%s'" % (expected[:idx],ellip,found[:idx],ellip)
        if casename != "":
            message = "test '%s': %s" % (casename,message)

        assert_equal(expected,found,message)

    def test_get_col1_text(self):
        for my_dict in self.match_dicts:
            yield self.check_equal, get_col1_text(my_dict), my_dict["col1"]

    def test_get_col2_text(self):
        for my_dict in self.match_dicts:
            yield self.check_equal, get_col2_text(my_dict), my_dict["col2"]

    def test_noargdoc_adds_attribute(self):
        def my_func():
            pass

        b = noargdoc(my_func)
        assert_true(b.__dict__["noargdoc"])

#     def test_get_subcommand_tables(self):
#         inp, expected, built = self.test_cases["with_subparsers"]
#         # look at output & test against known RST
#         assert False

    @staticmethod
    def check_list_equal(l1,l2,test_name):
        print("Checking list equality for %s" % test_name)
        mismatched = []
        for n, (line1,line2) in enumerate(zip(l1,l2)):
            if isinstance(line1,str):
                line1 = line1.decode("utf-8")
            if isinstance(line2,str):
                line2 = line2.decode("utf-8")
            if line1 != line2:
                mismatched.append(n)
        
        message = ""
        if len(mismatched) > 0:
            message  = "-"*75 + "\n"
            message  = "test '%s': Lists differ at lines %s\n" % (test_name,(", ").join([str(X) for X in mismatched]))
            message += "List 1:\n"
            for n in mismatched:
                message += "%s\t%s\n" % (n,l1[n])

            message += "List 2:\n"
            for n in mismatched:
                message += "%s\t%s\n" % (n,l2[n])

            message = "-"*75 + "\n"
        
        assert_equal(len(mismatched),0,message)
        
    def test_format_argparser_to_docstring(self):
        # look at output & test against known RST
        app = FakeApp(outdir=self.optdict["outdir"])
        for k in self.test_cases:
            testname = "test_format_argparser_to_docstring '%s'" % k            
            mod, expected, _ = self.test_cases[k]
            with open(expected) as f:
                expected_lines = f.read().split("\n")
            f.close()

            buf = cStringIO.StringIO()
            old_out = sys.stdout
            sys.stdout = buf
            try:
                mod.main(["--help"])
            except SystemExit as e:
                if e.code != 0:
                    raise(AssertionError("Exit code for '%s --help' was %s instead of zero" % (mod.__name__,e.code)))
            sys.stdout = old_out
            
            buf.seek(0)
            lines = buf.read().split("\n")

            found_lines = format_argparser_to_docstring(app,mod,lines,get_patterns())
            
            if k == "noargdoc":
                n1 = 0
                expected_lines = []
            else:
                for n1, line in enumerate(expected_lines):
                    if line.startswith("Command-line arguments"):
                        break

            for n2, line in enumerate(found_lines):
                if line.startswith("Command-line arguments"):
                    break

            yield self.check_list_equal, expected_lines[n1:], found_lines[n2:], testname

    @attr(kind="functional")
    def test_post_process_automodule(self):
        self.run_builder()
        for k, (_,expected,built) in self.test_cases.items():
            if k == "noargdoc":
                continue
            with open(expected) as f:
                expected_lines = f.read().split("\n")

            with open(built) as f:
                built_lines = f.read().split("\n")

            testname = "test_post_process_automodule '%s'" % k
            yield self.check_equal, expected_lines, built_lines, testname

    def test_post_process_automodule_emits_event(self):
        for k, (mod,_,_) in self.test_cases.items():
            testname = "test_post_process_automodule_emits_event '%s'" % k
            app = FakeApp(outdir=self.optdict["outdir"])
            options = {}
            expected = ["argdoc-process-docstring"]
            _ = post_process_automodule(app,"module",mod.__name__,mod,options,[])
            yield self.check_equal, expected, app.emitted, testname

class Record(object):
    """Proxy object that allows addition of arbitrary properties"""
    def __init__(self):
        pass

class FakeApp(object):
    """Proxy for a Sphinx application object. Implements minimial methods
    required for us to test functions in :mod:`argdoc.ext` that require
    a Sphinx application instance
    """
    def __init__(self,argdoc_main_func="main",argdoc_save_rst=True,outdir="/tmp/"):
        self.config = Record()
        self.config.argdoc_main_func = argdoc_main_func
        self.config.argdoc_save_rst = argdoc_save_rst
        self.outdir  = outdir
        self.emitted = []

    def warn(self,*args,**kwargs):
        pass

    def debug(self,*args,**kwargs):
        pass

    def emit(self,*args,**kwargs):
        """Simulate `emit` method. Save event name in `self.emitted` at each call"""
        self.emitted.append(args[0])
