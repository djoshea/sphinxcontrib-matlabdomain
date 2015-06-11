'''
Created on Jun 9, 2015

@author: joshua
'''
from nose.tools import assert_equal, assert_true
from argdoc.ext import patterns


class TestPatterns():
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
        cls.test_cases["opt_only"] = [("  --help",('--help', None)),
                                      ("  -h",('-h', None)),
                                      ("  -h, --help",('-h, --help', ', --help')),
                                      ]
        cls.test_cases["opt_plus_args"] = [("  -o FILENAME, --out FILENAME",('-o', None, ' FILENAME')),
                                           ("  -o FILENAME",('-o', None, ' FILENAME')),
                                           ("  --out FILENAME",('--out', None, ' FILENAME')),
                                           ("-o FILENAME, --out FILENAME",None),
                                           ("-o FILENAME",None),
                                           ("--out FILENAME",None),                               
                                           ("  -n M M, --num M M",('-n', None, ' M')),
                                           ("  -n M M",('-n', None, ' M')),
                                           ("  --num M M",('--num', None, ' M')),
                                           ("-n M M, --num M M",None),
                                           ("-n M M",None),
                                           ("--num M M",None),
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
    
    def test_all(self):
        for name, cases in self.test_cases.items():
            for inp,expected in cases:
                yield TestPatterns.check_match, name, patterns[name], inp, expected
# 
# 
# def test_process_argparser_help():
#     assert False
# 
# def test_add_args_to_module_docstring():
#     assert False
#
