#!/usr/bin/env python
"""Test suite for :obj:`argdoc`
"""
import argparse
from nose.tools import assert_equal, assert_true
from argdoc.ext import patterns

__date__ = "2015-06-09"


#===============================================================================
# INDEX: test cases
#===============================================================================

_SIMPLE_DESC1="""
Simple help for an argparser test for :py:class:`argparse.ArgumentParser`.
We'll put in all kinds of things that look like --options.

Examples:
  --option 1      Some option description

  -k, --key 2     Some other description
"""

def get_simple_parser():
    parser = argparse.ArgumentParser(description=_SIMPLE_DESC1,
                                     formater_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("positional1",help="First positional argument (really important)",type=str)
    parser.add_argument("positional2",help="Second positional argument, -with hyphens --and things that look like them.",type=str)
    parser.add_argument("positional3_no_desc")

    parser.add_argument("-k",dest="keyword1",help="First kwarg",metavar="N")
    parser.add_argument("--keyword2",dest="keyword2",help="Second kwarg",metavar="N")
    parser.add_argument("--keyword3",help="Third kwarg (Default: M M)",nargs=2)
    parser.add_argument("--keyword4_no_desc",type=str,metavar="X")
    parser.add_argument("--choices1",choices=("c1","c2","c3"),help="Make hcoices")
    parser.add_argument("--choices2",choices=("d2","d3"))
    parser.add_argument("--reallyreallyreallyreallylongoption",metavar="long_option_argument",help="This help should appear on the next line")
    return parser.format_help().split("\n")

def get_optiongroup_parser():
    parser = argparse.ArgumentParser(description=_SIMPLE_DESC1,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    return parser

class TestArgdoc():
    """Test case for functions defined in :mod:`argdoc.ext`"""

    @classmethod
    def setUpClass(cls):
        cls.test_cases = {}
        cls.test_cases["section_title"] = [("optional arguments:", ("optional arguments",)),
                                           ("optional arguments: ",None),
                                           (" optional arguments:",None),
                                           ("optional: arguments:",("optional: arguments",)),
                                           ("positional arguments:",("positional arguments",)),
                                           ("some long string (with parentheses):",("some long string (with parentheses)",)),
                                           ]
        cls.test_cases["opt_only"] = [("  --help",    ('--help', None)),
                                      ("  -h",        ('-h', None)),
                                      ("  -h, --help",('-h, --help', ', --help')),
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
        cls.test_cases["opt_plus_args"] = [("  -o FILENAME, --out FILENAME",('-o', ' FILENAME', '--out', ' FILENAME')),
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
        cls.test_cases["opt_plus_desc"] = [("  -h, --help            show this help message and exit",('-h, --help', ', --help', 'show this help message and exit')),
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
        cls.test_cases["opt_plus_args_desc"] = [
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
        cls.test_cases["subcommand_names"] = {("  {one,another,four,five}",("one,another,four,five",)),
                                              ("  {one,another,four}",("one,another,four",)),
                                              ("  {one,another}",("one,another",)),
                                              ("  {just_one}",("just_one",)),
                                              ("{one,another,four,five}",None),
                                              ("{one,another,four}",None),
                                              ("{one,another}",None),
                                              ("{just_one}",None),                                              
                                              }
        cls.test_cases["continue_desc"] = []
        cls.test_cases["section_desc"] = []

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
        for name, cases in self.test_cases.items():
            for inp,expected in cases:
                yield self.check_match, name, patterns[name], inp, expected

    def test_process_single_or_sub_program(self):
        assert False

    def test_process_subcommands(self):
        assert False

    def test_process_argparser_help(self):
        assert False
     
    def test_add_args_to_module_docstring(self):
        assert False

