# -*- coding: utf-8 -*-
"""
    sphinxcontrib.mat_types
    ~~~~~~~~~~~~~~~~~~~~~~~

    Types for MATLAB.

    :copyright: Copyright 2014 Mark Mikofski
    :license: BSD, see LICENSE for details.
"""

import os
import re
import sys
from copy import copy
from collections import OrderedDict

# Pygments MatlabLexer is in pygments.lexers.math, but recommended way to load
# is from lexers, which has LEXERS dictionary, which PyDev doesn't see.
from pygments.lexers import MatlabLexer  # @UnresolvedImport
# PyDev doesn't see Token methods and subtypes that are generated at runtime
from pygments.token import Token

MAT_DOM = 'MATLAB-domain'
__all__ = ['MatObject', 'MatModule', 'MatFunction', 'MatClass',  \
           'MatClassMemberGroup', \
           'MatProperty', 'MatMethod', 'MatScript', 'MatException', \
           'MatModuleAnalyzer', 'MAT_DOM']

# TODO: use `self.tokens.pop()` instead of idx += 1, see MatFunction

# XXX: Don't use `type()` or metaclasses. Not trivial to create metafunctions.
# XXX: Some special attributes **are** required even though `getter()` methods
# are also used.

# create some MATLAB objects
# TODO: +packages & @class folders
# TODO: subfunctions (not nested) and private folders/functions/classes
# TODO: script files

class MatObject(object):
    """
    Base MATLAB object to which all others are subclassed.

    :param name: Name of MATLAB object.
    :type name: str

    MATLAB objects can be :class:`MatModule`, :class:`MatFunction` or
    :class:`MatClass`. :class:`MatModule` are just folders that define a psuedo
    namespace for :class:`MatFunction` and :class:`MatClass` in that folder.
    :class:`MatFunction` and :class:`MatClass` must begin with either
    ``function`` or ``classdef`` keywords.
    """

    @staticmethod
    def dbg(msg, *args):
        """
        Alternate for sphinx_dbg for test-mode.
        """
        print '\t<test-mode>\n' + msg % args

    basedir = None
    sphinx_env = None
    sphinx_app = None
    sphinx_dbg = dbg

    def __init__(self, name):
        #: name of MATLAB object
        self.name = name

    @property
    def __name__(self):
        return self.name

    def __repr__(self):
        # __str__() method not required, if not given, then __repr__() used
        return '<%s: "%s">' % (self.__class__.__name__, self.name)

    def getter(self, name, *defargs):
        if name == '__name__':
            return self.__name__
        elif len(defargs) == 0:
            warn_msg = '[%s] WARNING Attribute "%s" was not found in %s.'
            MatObject.sphinx_dbg(warn_msg, MAT_DOM, name, self)
            return None
        elif len(defargs) == 1:
            return defargs[0]
        else:
            return defargs

    @staticmethod
    def matlabify(objname):
        """
        Makes a MatObject.

        :param objname: Name of object to matlabify without file extension.
        :type objname: str

        Assumes that object is contained in a folder described by a namespace
        composed of modules and packages connected by dots, and that the top-
        level module or package is in the Sphinx config value
        ``matlab_src_dir`` which is stored locally as
        :attr:`MatObject.basedir`. For example:
        ``my_project.my_package.sub_pkg.MyClass`` represents either a folder
        ``basedir/my_project/my_package/sub_pkg/MyClass`` or an mfile
        ``basedir/my_project/my_package/sub_pkg/MyClass.m``. If there is both a
        folder and an mfile with the same name, the folder takes precedence
        over the mfile.
        """
        # no object name given
        if not objname:
            return None
        # matlab modules are really packages
        package = objname  # for packages it's namespace of __init__.py
        # convert namespace to path
        objname = objname.replace('.', os.sep)  # objname may have dots
        # separate path from file/folder name
        path, name = os.path.split(objname)
        # make a full path out of basedir and objname
        fullpath = os.path.join(MatObject.basedir, objname)  # objname fullpath
        # package folders imported over mfile with same name
        if os.path.isdir(fullpath):
            mod = sys.modules.get(package)
            if mod:
                msg = '[%s] mod %s already loaded.'
                MatObject.sphinx_dbg(msg, MAT_DOM, package)
                return mod
            else:
                msg = '[%s] matlabify %s from\n\t%s.'
                MatObject.sphinx_dbg(msg, MAT_DOM, package, fullpath)
                return MatModule(name, fullpath, package)  # import package
        elif os.path.isfile(fullpath + '.m'):
            mfile = fullpath + '.m'
            return MatObject.parse_mfile(mfile, name, path)  # parse mfile
        return None

    @staticmethod
    def parse_mfile(mfile, name, path):
        """
        Use Pygments to parse mfile to determine type: function or class.

        :param mfile: Full path of mfile.
        :type mfile: str
        :param name: Name of :class:`MatObject`.
        :type name: str
        :param path: Path of module containing :class:`MatObject`.
        :type path: str
        :returns: :class:`MatObject` that represents the type of mfile.

        Assumes that the first token in the file is either one of the keywords:
        "classdef" or "function" otherwise it is assumed to be a script.
        """
        # use Pygments to parse mfile to determine type: function/classdef
        # read mfile code

        print 'Reading mfile %s' % (mfile)

        with open(mfile, 'r') as code_f:
            code = code_f.read().replace('\r\n', '\n')  # repl crlf with lf
        # functions must be contained in one line, no ellipsis, classdef is OK
        pat = r"""^[ \t]*function[ \t.\n]*  # keyword (function)
                  (\[?[\w, \t.\n]*\]?)      # outputs: group(1)
                  [ \t.\n]*=[ \t.\n]*       # punctuation (eq)
                  (\w+)[ \t.\n]*            # name: group(2)
                  \(?([\w, \t.\n]*)\)?"""   # args: group(3)
        pat = re.compile(pat, re.X | re.MULTILINE)  # search start of every line
        # replacement function
        def repl(m):
            # replace any ellipsis found in function signatures
            retv = m.group(0).replace('...\n', ' ')
            # if no args and doesn't end with parentheses, append "()"
            if not (m.group(3) or m.group(0).endswith('()')):
                retv = retv.replace(m.group(2), m.group(2) + "()")
            return retv
        code = pat.sub(repl, code)  # search for functions and apply replacement
        msg = '[%s] replaced ellipsis & appended parentheses in function signatures'
        MatObject.sphinx_dbg(msg, MAT_DOM)
        tks = list(MatlabLexer().get_tokens(code))  # tokenenize code

        # tag with line numbers
        lineno = 1
        linenum_by_token = []
        for tktype, token in tks:
            linenum_by_token.append(lineno)
            lineno += token.count('\n')

        modname = path.replace(os.sep, '.')  # module name
        # assume that functions and classes always start with a keyword
        if tks[0] == (Token.Keyword, 'function'):
            MatObject.sphinx_dbg('[%s] parsing function %s from %s.', MAT_DOM,
                                 name, modname)
            obj = MatFunction(name, modname, tks, linenum_by_token[0])
            obj.code = code
            return obj
        elif tks[0] == (Token.Keyword, 'classdef'):
            MatObject.sphinx_dbg('[%s] parsing classdef %s from %s.', MAT_DOM,
                                 name, modname)
            obj = MatClass(name, modname, tks, linenum_by_token)
            obj.code = code
            return obj
        else:
            # it's a script file
            obj = MatScript(name, modname, tks, linenum_by_token)
            obj.code = code
            return obj
        return None

# TODO: get docstring and __all__ from contents.m if exists
class MatModule(MatObject):
    """
    All MATLAB modules are packages. A package is a folder that serves as the
    namespace for any :class:`MatObjects` in the package folder. Sphinx will
    treats objects without a namespace as builtins, so all MATLAB projects
    should be packaged in a folder so that they will have a namespace. This
    can also be accomplished by using the MATLAB +folder package scheme.

    :param name: Name of :class:`MatObject`.
    :type name: str
    :param path: Path of folder containing :class:`MatObject`.
    :type path: str
    """
    def __init__(self, name, path, package):
        super(MatModule, self).__init__(name)
        #: Path to module on disk, path to package's __init__.py
        self.path = path
        #: name of package (full path from basedir to module)
        self.package = package
        # add module to system dictionary
        sys.modules[package] = self

    def safe_getmembers(self):
        results = []
        for key in os.listdir(self.path):
            # make full path
            path = os.path.join(self.path, key)
            # don't visit vcs directories
            if os.path.isdir(path) and key in ['.git', '.hg', '.svn', '.bzr']:
                continue
            # only visit mfiles
            if os.path.isfile(path) and not key.endswith('.m'):
                continue
            # trim file extension
            if os.path.isfile(path):
                key, _ = os.path.splitext(key)
            if not results or key not in zip(*results)[0]:
                value = self.getter(key, None)
                if value:
                    results.append((key, value))
        results.sort()
        return results

    @property
    def __doc__(self):
        return None

    @property
    def __all__(self):
        results = self.safe_getmembers
        if results:
            results = zip(*self.safe_getmembers)[0]
        return results

    @property
    def __path__(self):
        return [self.path]

    @property
    def __file__(self):
        return self.path

    @property
    def __package__(self):
        return self.package

    def getter(self, name, *defargs):
        """
        :class:`MatModule` ``getter`` method to get attributes.
        """
        if name == '__name__':
            return self.__name__
        elif name == '__doc__':
            return self.__doc__
        elif name == '__all__':
            return self.__all__
        elif name == '__file__':
            return self.__file__
        elif name == '__path__':
            return self.__path__
        elif name == '__package__':
            return self.__package__
        elif name == '__module__':
            msg = '[%s] mod %s is a package does not have __module__.'
            MatObject.sphinx_dbg(msg, MAT_DOM, self)
            return None
        else:
            if hasattr(self, name):
                msg = '[%s] mod %s already has attr %s.'
                MatObject.sphinx_dbg(msg, MAT_DOM, self, name)
                return getattr(self, name)
            attr = MatObject.matlabify('.'.join([self.package, name]))
            if attr:
                setattr(self, name, attr)
                msg = '[%s] attr %s imported from mod %s.'
                MatObject.sphinx_dbg(msg, MAT_DOM, name, self)
                return attr
            else:
                super(MatModule, self).getter(name, *defargs)


class MatMixin(object):
    """
    Methods to comparing and manipulating tokens in :class:`MatFunction` and
    :class:`MatClass`.
    """
    def _tk_eq(self, idx, token):
        """
        Returns ``True`` if token keys are the same and values are equal.

        :param idx: Index of token in :class:`MatObject`.
        :type idx: int
        :param token: Comparison token.
        :type token: tuple
        """
        return (self.tokens[idx][0] is token[0] and
                self.tokens[idx][1] == token[1])

    def _tk_ne(self, idx, token):
        """
        Returns ``True`` if token keys are not the same or values are not
        equal.

        :param idx: Index of token in :class:`MatObject`.
        :type idx: int
        :param token: Comparison token.
        :type token: tuple
        """
        return (self.tokens[idx][0] is not token[0] or
                self.tokens[idx][1] != token[1])

    def _eotk(self, idx):
        """
        Returns ``True`` if end of tokens is reached.
        """
        return idx >= len(self.tokens)

    def _blanks(self, idx):
        """
        Returns number of blank text tokens.

        :param idx: Token index.
        :type idx: int
        """
        # idx0 = idx  # original index
        # while self._tk_eq(idx, (Token.Text, ' ')): idx += 1
        # return idx - idx0  # blanks
        return self._indent(idx)

    def _whitespace(self, idx):
        """
        Returns number of whitespaces text tokens, including blanks, newline
        and tabs.

        :param idx: Token index.
        :type idx: int
        """
        idx0 = idx  # original index
        while self.tokens[idx][1].isspace():
            idx += 1
        return idx - idx0  # whitespace

    def _skip_whitespace(self, idx):
        while self.tokens[idx][1].isspace():
            idx += 1
        return idx

    def _indent(self, idx):
        """
        Returns indentation tabs or spaces. No indentation is zero.

        :param idx: Token index.
        :type idx: int
        """
        idx0 = idx  # original index
        while (self.tokens[idx][0] is Token.Text and
               self.tokens[idx][1] in [' ', '\t']):
            idx += 1
        return idx - idx0  # indentation

    def gather_docstring(self, idx):
        idx = self._skip_whitespace(idx)
        docstring = []
        while self.tokens[idx][0] is Token.Comment:
            docstring += self.tokens[idx][1].lstrip('%') + '\n'  # concatenate
            idx += 1
            idx = self._skip_whitespace(idx)

        docstring = ''.join(docstring)
        return (docstring, idx)


class MatFunction(MatObject):
    """
    A MATLAB function.

    :param name: Name of :class:`MatObject`.
    :type name: str
    :param modname: Name of folder containing :class:`MatObject`.
    :type modname: str
    :param tokens: List of tokens parsed from mfile by Pygments.
    :type tokens: list
    """
    # MATLAB keywords that increment keyword-end pair count
    mat_kws = zip((Token.Keyword,) * 5,
                  ('if', 'while', 'for', 'switch', 'try'))

    def __init__(self, name, modname, tokens, linestart, abstract=False):
        super(MatFunction, self).__init__(name)
        #: Path of folder containing :class:`MatObject`.
        self.module = modname
        #: List of tokens parsed from mfile by Pygments.
        self.tokens = tokens
        #: docstring
        self.docstring = ''
        #: output args
        self.retv = None
        #: input args
        self.args = None
        #: remaining tokens after main function is parsed
        self.rem_tks = None

        self.abstract = abstract

        self.source_linestart = linestart

        # =====================================================================
        # parse tokens
        # XXX: Pygments always reads MATLAB function signature as:
        # [(Token.Keyword, 'function'),  # any whitespace is stripped
        #  (Token.Text.Whitesapce, ' '),  # spaces and tabs are concatenated
        #  (Token.Text, '[o1, o2]'),  # if there are outputs, they're all
        #                               concatenated w/ or w/o brackets and any
        #                               trailing whitespace
        #  (Token.Punctuation, '='),  # possibly an equal sign
        #  (Token.Text.Whitesapce, ' '),  # spaces and tabs are concatenated
        #  (Token.Name.Function, 'myfun'),  # the name of the function
        #  (Token.Punctuation, '('),  # opening parenthesis
        #  (Token.Text, 'a1, a2',  # if there are args, they're concatenated
        #  (Token.Punctuation, ')'),  # closing parenthesis
        #  (Token.Text.Whitesapce, '\n')]  # all whitespace after args
        # XXX: Pygments does not tolerate MATLAB continuation ellipsis!
        tks = copy(self.tokens)  # make a copy of tokens
        tks.reverse()  # reverse in place for faster popping, stacks are LiLo
        # =====================================================================
        # parse function signature
        # function [output] = name(inputs)
        # % docstring
        # =====================================================================
        # check function keyword
        func_kw = tks.pop()  # function keyword
        if not self.abstract:
            if func_kw[0] is not Token.Keyword or func_kw[1].strip() != 'function':
                raise TypeError('Object is not a function. Expected a function. (%s : %d)' % (name, linestart))
                # TODO: what is a better error here?
            # skip blanks and tabs
            if tks.pop()[0] is not Token.Text.Whitespace:  # @UndefinedVariable
                raise TypeError('Expected a whitespace after function keyword.')
                # TODO: what is a better error here?
        else:
            # put it back, this is the function name for abstract methods
            tks.append(func_kw)

        # =====================================================================
        # output args
        retv = tks.pop()

        if self.abstract: # need to handle this differently since the lexer isn't quite up to the task
            if retv[0] is Token.Text or retv[0] is Token.Name:
                self.retv = [rv.strip() for rv in retv[1].strip('[ ]').split(',')]
                if len(self.retv) == 1:
                    # check if return is empty
                    if not self.retv[0]:
                        self.retv = None
                    # check if return delimited by whitespace
                    elif ' ' in self.retv[0] or '\t' in self.retv[0]:
                        self.retv = [rv for rv_tab in self.retv[0].split('\t')
                                     for rv in rv_tab.split(' ')]

                # check for whitespace before equal sign
                wht = tks.pop()
                if wht[0] is not Token.Text.Whitespace and not wht[1].isspace():  # @UndefinedVariable
                    tks.append(wht)  # if not whitespace, put it back in list
                next = tks.pop()
                if next != (Token.Punctuation, '='):
                    # then this must be the function name, push everything back on to the token stack
                    tks.append(next)
                    tks.append(retv)
                    self.retv = None
                else:
                    # check for whitespace after equal sign
                    wht = tks.pop()
                    if wht[0] is not Token.Text.Whitespace and not wht[1].isspace():  # @UndefinedVariable
                        tks.append(wht)  # if not whitespace, put it back in list
            elif retv[1] == '[':
                # handle the multiple ret vals case
                retv = tks.pop()
                self.retv = []
                while retv[1] != ']':
                    if retv[0] is Token.Text or retv[0] is Token.Name:
                        self.retv += [rv.strip() for rv in retv[1].strip('[ ]').split(',')]
                    retv = tks.pop()
                    while retv[1].isspace() or retv[1] == ',':
                        retv = tks.pop()

                next = tks.pop()
                while next[1].isspace():
                    next = tks.pop()

                if next != (Token.Punctuation, '='):
                    raise Exception('Expecting = after output argument list for abstract method')

            elif retv[0] is Token.Name.Function or self.abstract:  # @UndefinedVariable
                tks.append(retv)
        else:
            if retv[0] is Token.Text:
                self.retv = [rv.strip() for rv in retv[1].strip('[ ]').split(',')]
                if len(self.retv) == 1:
                    # check if return is empty
                    if not self.retv[0]:
                        self.retv = None
                    # check if return delimited by whitespace
                    elif ' ' in self.retv[0] or '\t' in self.retv[0]:
                        self.retv = [rv for rv_tab in self.retv[0].split('\t')
                                     for rv in rv_tab.split(' ')]
                if tks.pop() != (Token.Punctuation, '='):
                    raise TypeError('Token after outputs should be Punctuation.')
                    # TODO: raise an matlab token error or what?
                # check for whitespace after equal sign
                wht = tks.pop()
                if wht[0] is not Token.Text.Whitespace:  # @UndefinedVariable
                    tks.append(wht)  # if not whitespace, put it back in list
            elif retv[0] is Token.Name.Function:  # @UndefinedVariable
                tks.append(retv)

        # create return value string for later inclusion in signature
        if self.retv is None:
            self.retann = None
        elif len(self.retv) > 1:
            self.retann = '[' + ', '.join(self.retv) + ']'
        else:
            self.retann = ''.join(self.retv)


        # =====================================================================
        # function name
        # strip intervening whitespace
        next = tks.pop()
        while next[1].isspace():
            next = tks.pop()
        func_name = next

        if func_name != (Token.Name.Function, self.name):  # @UndefinedVariable
            if isinstance(self, MatMethod):
                self.name = func_name[1]
            else:
                errmsg = 'Unexpected function name: "%s".' % func_name[1]
                raise Exception(errmsg)
                # TODO: create mat_types or tokens exceptions!
        # =====================================================================
        # input args
        next = tks.pop()
        if next == (Token.Punctuation, '('):
            args = tks.pop()
            if args[0] is Token.Text or (self.abstract and args[0] is Token.Name):
                self.args = [arg.strip() for arg in args[1].split(',')]\
            # no arguments given
            elif args == (Token.Punctuation, ')'):
                tks.append(args)  # put closing parenthesis back in stack

            # check if function args parsed correctly
            next = tks.pop()
            while self.abstract and next[0] is Token.Punctuation and next[1].strip() == ',':
                # extra args due to lexer not working for Abstract methods
                next = tks.pop()
                while next[1].isspace():
                    next = tks.pop()
                if next[0] is Token.Text or next[0] is Token.Name:
                    self.args += [arg.strip() for arg in next[1].split(',')]
                    next = tks.pop()
                    while next[1].isspace():
                        next = tks.pop()

            if next != (Token.Punctuation, ')'):
                raise TypeError('Token after outputs should be Punctuation. (%s : after %d)' % (name, linestart))
                # TODO: raise an matlab token error or what?
        # skip blanks and tabs
        next = tks.pop()
        if next[0] is not Token.Text.Whitespace and not next[1].isspace() and \
                not (self.abstract and next[0] is Token.Punctuation and next[1] == ';'):  # @UndefinedVariable
            raise TypeError('Expected a whitespace after input args. (%s : after %d)' % (name, linestart))
            # TODO: what is a better error here?
        # =====================================================================
        # docstring
        docstring = []
        next = tks.pop()
        while next[1].isspace():
            next = tks.pop()
        while next[0] is Token.Comment:
            docstring += next[1].lstrip('%') + '\n'  # concatenate
            next = tks.pop()
            while next[1].isspace():
                next = tks.pop()

        self.docstring = ''.join(docstring)
        tks.append(next)
        # try:x
        #     docstring = tks.pop()
        # except IndexError:
        #     docstring = None
        # while docstring and docstring[0] is Token.Comment:
        #     self.docstring += docstring[1].lstrip('%') + '\n'  # concatenate
        #     try:
        #         wht = tks.pop()  # skip whitespace
        #     except IndexError:
        #         break
        #     while wht in zip((Token.Text,) * 3, (' ', '\t', '\n')):
        #         try:
        #             wht = tks.pop()
        #         except IndexError:
        #             break
        #     docstring = wht  # check if Token is Comment

        if not self.abstract:
            # =====================================================================
            # main body
            # find Keywords - "end" pairs
            kw = tks.pop()  # last token
            lastkw = 0  # set last keyword placeholder
            kw_end = 1  # count function keyword
            while kw_end > 0:
                # increment keyword-end pairs count
                if kw in MatFunction.mat_kws:
                    kw_end += 1
                # nested function definition
                elif kw[0] is Token.Keyword and kw[1].strip() == 'function':
                    kw_end += 1
                # decrement keyword-end pairs count but
                # don't decrement `end` if used as index
                elif kw == (Token.Keyword, 'end') and not lastkw:
                    kw_end -= 1
                # save last punctuation
                elif kw in zip((Token.Punctuation,) * 2, ('(', '{')):
                    lastkw += 1
                elif kw in zip((Token.Punctuation,) * 2, (')', '}')):
                    lastkw -= 1
                try:
                    kw = tks.pop()
                except IndexError:
                    break
            tks.append(kw)  # put last token back in list
            # if there are any tokens left save them
            if len(tks) > 0:
                self.rem_tks = tks  # save extra tokens
        else:
            self.rem_tks = tks

    @property
    def __doc__(self):
        return unicode(self.docstring)

    @property
    def __module__(self):
        return self.module

    def getter(self, name, *defargs):
        if name == '__name__':
            return self.__name__
        elif name == '__doc__':
            return self.__doc__
        elif name == '__module__':
            return self.__module__
        else:
            super(MatFunction, self).getter(name, *defargs)


class MatClass(MatMixin, MatObject):
    """
    A MATLAB class definition.

    :param name: Name of :class:`MatObject`.
    :type name: str
    :param path: Path of folder containing :class:`MatObject`.
    :type path: str
    :param tokens: List of tokens parsed from mfile by Pygments.
    :type tokens: list
    """
    #: dictionary of MATLAB class "attributes"
    # http://www.mathworks.com/help/matlab/matlab_oop/class-attributes.html
    cls_attr_types = {'Abstract': bool, 'AllowedSubclasses': list,
                      'ConstructOnLoad': bool, 'HandleCompatible': bool,
                      'Hidden': bool, 'InferiorClasses': list, 'Sealed': bool}
    prop_attr_types = {'AbortSet': bool, 'Abstract': bool, 'Access': list,
                       'Constant': bool, 'Dependent': bool, 'GetAccess': list,
                       'GetObservable': bool, 'Hidden': bool,
                       'SetAccess': list, 'SetObservable': bool,
                       'Transient': bool, 'ClassSetupParameter': bool,
                       'MethodSetupParameter': bool, 'TestParameter': bool}
    meth_attr_types = {'Abstract': bool, 'Access': list, 'Hidden': bool,
                       'Sealed': list, 'Static': bool, 'Test': bool,
                       'TestClassSetup': bool, 'TestMethodSetup': bool,
                       'TestClassTeardown': bool, 'TestMethodTeardown': bool,
                       'ParameterCombination': bool}

    def __init__(self, name, modname, tokens, linenum_by_token):
        super(MatClass, self).__init__(name)
        #: Path of folder containing :class:`MatObject`.
        self.module = modname
        #: List of tokens parsed from mfile by Pygments.
        self.tokens = tokens
        #: dictionary of class attributes
        self.attrs = {}
        #: list of class superclasses
        self.bases = []
        #: docstring
        self.docstring = ''
        #: dictionary of class properties
        self.properties = OrderedDict()
        #: dictionary of class methods
        self.methods = OrderedDict()
        # list of MatClassMemberGroups which themselves contain methods and properties
        self.member_groups = []

        self.linenum_by_token = linenum_by_token
        self.source_linestart = linenum_by_token[0]

        # will be set to true if an enumeration block is found within
        self.is_enum = False

        #: remaining tokens after main class definition is parsed
        self.rem_tks = None

        # =====================================================================
        # parse tokens
        # TODO: use generator and next() instead of stepping index!
        idx = 0  # token index
        # check classdef keyword
        if self._tk_ne(idx, (Token.Keyword, 'classdef')):
            raise TypeError('Object is not a class. Expected a class.')
        idx += 1
        # TODO: allow continuation dots "..." in signature
        # parse classdef signature
        # classdef [(Attributes [= true], Attributes [= {}] ...)] name ...
        #   [< bases & ...]
        # % docstring
        # =====================================================================
        # class "attributes"
        self.attrs, idx = self.attributes(idx, MatClass.cls_attr_types)
        # =====================================================================
        # classname
        idx += self._blanks(idx)  # skip blanks
        if self._tk_ne(idx, (Token.Name, self.name)):
            errmsg = 'Unexpected class name: "%s".' % self.tokens[idx][1]
            raise Exception(errmsg)
            # TODO: create exception classes
        idx += 1
        idx += self._blanks(idx)  # skip blanks
        # =====================================================================
        # super classes
        if self._tk_eq(idx, (Token.Operator, '<')):
            idx += 1
            # newline terminates superclasses
            while self._tk_ne(idx, (Token.Text, '\n')):
                idx += self._blanks(idx)  # skip blanks
                # concatenate base name
                base_name = ''
                while not self._whitespace(idx):
                    base_name += self.tokens[idx][1]
                    idx += 1
                # if newline, don't increment index
                if self._tk_ne(idx, (Token.Text, '\n')):
                    idx += 1
                if base_name:
                    self.bases.append(base_name)
                idx += self._blanks(idx)  # skip blanks
                # continue to next super class separated by &
                if self._tk_eq(idx, (Token.Operator, '&')):
                    idx += 1
            idx += 1  # end of super classes
        # newline terminates classdef signature
        elif self._tk_eq(idx, (Token.Text, '\n')):
            idx += 1  # end of classdef signature
        # =====================================================================
        # docstring
        # Must be immediately after class and indented
        indent = self._indent(idx)  # calculation indentation
        if indent:
            idx += indent
            # concatenate docstring
            while self.tokens[idx][0] is Token.Comment:
                self.docstring += self.tokens[idx][1].lstrip('%')
                idx += 1
                # append newline to docstring
                if self._tk_eq(idx, (Token.Text, '\n')):
                    self.docstring += self.tokens[idx][1]
                    idx += 1
                # skip tab
                indent = self._indent(idx)  # calculation indentation
                if indent:
                    idx += indent
        elif self.tokens[idx][0] is Token.Comment:
            raise Exception('Comments must be indented. (%s : %d)' % (name, linenum_by_token[idx]))
            # TODO: add to matlab domain exceptions
        # =====================================================================
        # properties & methods blocks
        # loop over code body searching for blocks until end of class
        while self._tk_ne(idx, (Token.Keyword, 'end')):
            # skip comments and whitespace
            while (self._whitespace(idx) or
                   self.tokens[idx][0] is Token.Comment):
                whitespace = self._whitespace(idx)
                if whitespace:
                    idx += whitespace
                else:
                    idx += 1
            # =================================================================
            # properties or enumeration blocks
            if self._tk_eq(idx, (Token.Keyword, 'properties')):
                source_linestart = self.linenum_by_token[idx]

                idx += 1
                # property "attributes"
                attr_dict, idx = self.attributes(idx, MatClass.prop_attr_types)

                # parse property group
                group_name, group_docstr, idx = self.parse_group_header_comment(idx)

                # create group to encompass methods
                uniq_name = self.name + '_member_group_%d' % (len(self.member_groups))
                member_group = MatClassMemberGroup(uniq_name, self, attr_dict,
                                                   'properties', group_name, group_docstr,
                                                   source_linestart)

                # Token.Keyword: "end" terminates properties & methods block
                while self._tk_ne(idx, (Token.Keyword, 'end')):
                    # skip comments and whitespace
                    while (self._whitespace(idx) or
                           self.tokens[idx][0] is Token.Comment):
                        whitespace = self._whitespace(idx)
                        if whitespace:
                            idx += whitespace
                        else:
                            idx += 1
                    # TODO: alternate multiline docstring before property
                    # with "%:" directive trumps docstring after property
                    if self.tokens[idx][0] is Token.Name:
                        prop_name = self.tokens[idx][1]
                        source_linestart = self.linenum_by_token[idx]
                        # self.properties[prop_name] = {'attrs': attr_dict}
                        idx += 1
                    # subtype of Name EG Name.Builtin used as Name
                    elif self.tokens[idx][0] in Token.Name.subtypes:  # @UndefinedVariable
                        prop_name = self.tokens[idx][1]
                        source_linestart = self.linenum_by_token[idx]
                        warn_msg = ' '.join(['[%s] WARNING %s.%s.%s is',
                                             'a Builtin Name'])
                        MatObject.sphinx_dbg(warn_msg, MAT_DOM, self.module,
                                             self.name, prop_name)

                        # self.properties[prop_name] = {'attrs': attr_dict}
                        idx += 1
                    elif self._tk_eq(idx, (Token.Keyword, 'end')):
                        idx += 1
                        break
                    # skip semicolon after property name, but no default
                    elif self._tk_eq(idx, (Token.Punctuation, ';')):
                        idx += 1
                        continue
                    else:
                        raise TypeError('Expected property.')
                    idx += self._blanks(idx)  # skip blanks

                    # Restricted property class
                    prop_restriction_class = ''
                    while self.tokens[idx][0] is Token.Name or self._tk_eq(idx, (Token.Punctuation, '.')):
                        prop_restriction_class += self.tokens[idx][1]
                        idx += 1
                    idx += self._blanks(idx)

                    # =========================================================
                    # default values
                    default = None
                    if self._tk_eq(idx, (Token.Punctuation, '=')):
                        idx += 1
                        idx += self._blanks(idx)  # skip blanks
                        # concatenate default value until newline or comment
                        default = ''
                        punc_ctr = 0  # punctuation placeholder
                        # keep reading until newline or comment
                        # only if all punctuation pairs are closed
                        # and comment is **not** continuation ellipsis
                        while ((self._tk_ne(idx, (Token.Text, '\n')) and
                                self.tokens[idx][0] is not Token.Comment) or
                               punc_ctr > 0 or
                               (self.tokens[idx][0] is Token.Comment and
                                self.tokens[idx][1].startswith('...'))):
                            token = self.tokens[idx]
                            # default has an array spanning multiple lines
                            if (token in zip((Token.Punctuation,) * 3,
                                ('(', '{', '['))):
                                punc_ctr += 1  # increment punctuation counter
                            # look for end of array
                            elif (token in zip((Token.Punctuation,) * 3,
                                       (')', '}', ']'))):
                                punc_ctr -= 1  # decrement punctuation counter
                            # Pygments treats continuation ellipsis as comments
                            # text from ellipsis until newline is in token
                            elif (token[0] is Token.Comment and
                                  token[1].startswith('...')):
                                idx += 1  # skip ellipsis comments
                                # include newline which should follow comment
                                if self._tk_eq(idx, (Token.Text, '\n')):
                                    default += '\n'
                                    idx += 1
                                continue
                            elif self._tk_eq(idx - 1, (Token.Text, '\n')):
                                idx += self._blanks(idx)
                                continue
                            default += token[1]
                            idx += 1
                        if self.tokens[idx][0] is not Token.Comment:
                            idx += 1
                        if default:
                            default = default.rstrip('; ')
                    # self.properties[prop_name].update(default)
                    # =========================================================
                    docstring, idx = self.gather_docstring(idx)

                    prop = MatProperty(prop_name, self, attr_dict, default, docstring, source_linestart)
                    prop.restriction_class = prop_restriction_class

                    # add to member_group
                    prop.member_group = member_group
                    member_group.properties[prop_name] = prop

                    # and directly to class
                    self.properties[prop_name] = prop

                    idx += self._whitespace(idx)
                idx += 1

                member_group.group_index = len(self.member_groups)
                self.member_groups.append(member_group)

            # =================================================================
            # enumeration block
            elif self._tk_eq(idx, (Token.Name, 'enumeration')):
                self.is_enum = True # mark this class as an enumeration block

                source_linestart = self.linenum_by_token[idx]

                idx += 1
                # property "attributes"
                attr_dict, idx = self.attributes(idx, MatClass.prop_attr_types)
                attr_dict['Enumeration'] = True

                # parse property group
                group_name, group_docstr, idx = self.parse_group_header_comment(idx)

                # create group to encompass methods
                uniq_name = self.name + '_member_group_%d' % (len(self.member_groups))
                member_group = MatClassMemberGroup(uniq_name, self, attr_dict,
                                                   'enumeration', group_name, group_docstr,
                                                   source_linestart)

                # Token.Keyword: "end" terminates properties & methods block
                while self._tk_ne(idx, (Token.Keyword, 'end')):
                    # skip comments and whitespace
                    while (self._whitespace(idx) or
                                   self.tokens[idx][0] is Token.Comment):
                        whitespace = self._whitespace(idx)
                        if whitespace:
                            idx += whitespace
                        else:
                            idx += 1
                    # TODO: alternate multiline docstring before property
                    # with "%:" directive trumps docstring after property
                    if self.tokens[idx][0] is Token.Name:
                        prop_name = self.tokens[idx][1]
                        source_linestart = self.linenum_by_token[idx]
                        # self.properties[prop_name] = {'attrs': attr_dict}
                        idx += 1
                    # subtype of Name EG Name.Builtin used as Name
                    elif self.tokens[idx][0] in Token.Name.subtypes:  # @UndefinedVariable
                        prop_name = self.tokens[idx][1]
                        source_linestart = self.linenum_by_token[idx]
                        warn_msg = ' '.join(['[%s] WARNING %s.%s.%s is',
                                             'a Builtin Name'])
                        MatObject.sphinx_dbg(warn_msg, MAT_DOM, self.module,
                                             self.name, prop_name)

                        # self.properties[prop_name] = {'attrs': attr_dict}
                        idx += 1
                    elif self._tk_eq(idx, (Token.Keyword, 'end')):
                        idx += 1
                        break
                    # skip semicolon after property name, but no default
                    elif self._tk_eq(idx, (Token.Punctuation, ';')):
                        idx += 1
                        continue
                    else:
                        raise TypeError('Expected property.')
                    idx += self._blanks(idx)  # skip blanks
                    # =========================================================
                    # defaults
                    default = None
                    if self._tk_eq(idx, (Token.Punctuation, '(')):
                        idx += 1
                        idx += self._blanks(idx)  # skip blanks
                        # concatenate default value until newline or comment
                        default = ''
                        punc_ctr = 1  # punctuation placeholder (start with one comment)
                        # keep reading until newline or comment
                        # only if all punctuation pairs are closed
                        # and comment is **not** continuation ellipsis
                        while ((self._tk_ne(idx, (Token.Text, '\n')) and
                                        self.tokens[idx][0] is not Token.Comment) or
                                       punc_ctr > 0 or
                                   (self.tokens[idx][0] is Token.Comment and
                                        self.tokens[idx][1].startswith('...'))):
                            token = self.tokens[idx]
                            # default has an array spanning multiple lines
                            if (token in zip((Token.Punctuation,) * 3,
                                             ('(', '{', '['))):
                                punc_ctr += 1  # increment punctuation counter
                            # look for end of array
                            elif (token in zip((Token.Punctuation,) * 3,
                                               (')', '}', ']'))):
                                punc_ctr -= 1  # decrement punctuation counter
                            # Pygments treats continuation ellipsis as comments
                            # text from ellipsis until newline is in token
                            elif (token[0] is Token.Comment and
                                      token[1].startswith('...')):
                                idx += 1  # skip ellipsis comments
                                # include newline which should follow comment
                                if self._tk_eq(idx, (Token.Text, '\n')):
                                    default += '\n'
                                    idx += 1
                                continue
                            elif self._tk_eq(idx - 1, (Token.Text, '\n')):
                                idx += self._blanks(idx)
                                continue

                            if punc_ctr > 0 or token[1] != ')': # don't include last )
                                default += token[1]
                            idx += 1
                        if self.tokens[idx][0] is not Token.Comment:
                            idx += 1
                        if default:
                            default = default.rstrip('; ')
                    # self.properties[prop_name].update(default)
                    # =========================================================
                    # docstring
                    # docstring = None
                    # if self.tokens[idx][0] is Token.Comment:
                    #     docstring = self.tokens[idx][1].lstrip('%')
                    #     idx += 1

                    docstring, idx = self.gather_docstring(idx)
                    prop = MatProperty(prop_name, self, attr_dict, default, source_linestart)

                    # add to member_group
                    prop.member_group = member_group
                    member_group.properties[prop_name] = prop

                    # and directly to class
                    self.properties[prop_name] = prop

                    idx += self._whitespace(idx)
                idx += 1

                member_group.group_index = len(self.member_groups)
                self.member_groups.append(member_group)

            # =================================================================
            # method blocks
            elif self._tk_eq(idx, (Token.Keyword, 'methods')):
                idx += 1
                source_linestart = self.linenum_by_token[idx]

                # method "attributes"
                attr_dict, idx = self.attributes(idx, MatClass.meth_attr_types)

                # parse methods group comment
                group_name, group_docstr, idx = self.parse_group_header_comment(idx)

                # create group to encompass methods
                uniq_name = self.name + '_member_group_%d' % (len(self.member_groups))
                member_group = MatClassMemberGroup(uniq_name, self, attr_dict,
                                                   'methods', group_name, group_docstr, source_linestart)

                # Token.Keyword: "end" terminates properties & methods block
                while self._tk_ne(idx, (Token.Keyword, 'end')):
                    group_name, group_docstring, idx = self.parse_group_header_comment(idx)

                    # skip comments and whitespace
                    while (self._whitespace(idx) or
                           self.tokens[idx][0] is Token.Comment):
                        whitespace = self._whitespace(idx)
                        if whitespace:
                            idx += whitespace
                        else:
                            idx += 1

                    if self._tk_eq(idx, (Token.Keyword, 'end')):
                        # in case end comes after whitespace
                        break

                    # handle normal non-abstract methods
                    if not member_group.abstract:
                        # skip methods defined in other files
                        meth_tk = self.tokens[idx]
                        source_linestart = self.linenum_by_token[idx]
                        if (meth_tk[0] is Token.Name or
                            meth_tk[0] is Token.Name.Function or
                            (meth_tk[0] is Token.Keyword and
                             meth_tk[1].strip() == 'function'
                             and self.tokens[idx+1][0] is Token.Name.Function) or
                            self._tk_eq(idx, (Token.Punctuation, '[')) or
                            self._tk_eq(idx, (Token.Punctuation, ']')) or
                            self._tk_eq(idx, (Token.Punctuation, '=')) or
                            self._tk_eq(idx, (Token.Punctuation, '(')) or
                            self._tk_eq(idx, (Token.Punctuation, ')')) or
                            self._tk_eq(idx, (Token.Punctuation, ','))):
                            msg = ['[%s] Skipping tokens for methods defined in separate files.',
                                   'token #%d: %r']
                            MatClass.sphinx_dbg('\n'.join(msg), MAT_DOM, idx, self.tokens[idx])
                            idx += 1 + self._whitespace(idx + 1)
                        elif self._tk_eq(idx, (Token.Keyword, 'end')):
                            idx += 1
                            break
                        else:
                            # find methods
                            meth = MatMethod(self.module, self.tokens[idx:],
                                             self, attr_dict, source_linestart)
                            # replace dot in get/set methods with underscore
                            if meth.name.split('.')[0] in ['get', 'set']:
                                meth.name = meth.name.replace('.', '_')
                                meth.is_getset = True
                            else:
                                meth.is_getset = False
                            idx += meth.reset_tokens()  # reset method tokens and index

                            # add to member group
                            meth.member_group = member_group
                            member_group.methods[meth.name] = meth

                            self.methods[meth.name] = meth  # and directly to class methods
                            idx += self._whitespace(idx)
                    else:
                        # find methods
                        source_linestart = self.linenum_by_token[idx]
                        meth = MatMethod(self.module, self.tokens[idx:],
                                         self, attr_dict, source_linestart)
                        # replace dot in get/set methods with underscore
                        if meth.name.split('.')[0] in ['get', 'set']:
                            meth.name = meth.name.replace('.', '_')
                            meth.is_getset = True
                        else:
                            meth.is_getset = False
                        idx += meth.reset_tokens()  # reset method tokens and index

                        # add to member group
                        meth.member_group = member_group
                        member_group.methods[meth.name] = meth

                        self.methods[meth.name] = meth  # and directly to class methods
                        idx += self._whitespace(idx)
                idx += 1

                member_group.group_index = len(self.member_groups)
                self.member_groups.append(member_group)

            elif self._tk_eq(idx, (Token.Keyword, 'end')):
                continue
            else:
                raise Exception('Unknown token %s' % (self.tokens[idx][1]))

        self.rem_tks = idx  # index of last token

    def attributes(self, idx, attr_types):
        """
        Retrieve MATLAB class, property and method attributes.
        """
        attr_dict = {}
        idx += self._blanks(idx)  # skip blanks
        # class, property & method "attributes" start with parenthesis
        if self._tk_eq(idx, (Token.Punctuation, '(')):
            idx += 1
            # closing parenthesis terminates attributes
            while self._tk_ne(idx, (Token.Punctuation, ')')):
                idx += self._blanks(idx)  # skip blanks

                k, attr_name = self.tokens[idx]  # split token key, value
                if k is Token.Name and attr_name in attr_types:
                    attr_dict[attr_name] = True  # add attibute to dictionary
                    idx += 1
                else:
                    errmsg = 'Unexpected attribute: "%s".' % attr_name
                    raise Exception(errmsg)
                    # TODO: make matlab exception
                idx += self._blanks(idx)  # skip blanks
                # continue to next attribute separated by commas
                if self._tk_eq(idx, (Token.Punctuation, ',')):
                    idx += 1
                    continue
                # attribute values
                elif self._tk_eq(idx, (Token.Punctuation, '=')):
                    idx += 1
                    idx += self._blanks(idx)  # skip blanks
                    # logical value
                    k, attr_val = self.tokens[idx]  # split token key, value
                    if (k is Token.Name and attr_val in ['true', 'false']):
                        if attr_val == 'false':
                            attr_dict[attr_name] = False
                        idx += 1
                    elif k is Token.Name or \
                        self._tk_eq(idx, (Token.Text, '?')):
                        # concatenate enumeration or meta class
                        enum_or_meta = self.tokens[idx][1]
                        idx += 1
                        while (self._tk_ne(idx, (Token.Text, ' ')) and
                               self._tk_ne(idx, (Token.Text, '\t')) and
                               self._tk_ne(idx, (Token.Punctuation, ',')) and
                               self._tk_ne(idx, (Token.Punctuation, ')'))):
                            enum_or_meta += self.tokens[idx][1]
                            idx += 1
                        if self._tk_ne(idx, (Token.Punctuation, ')')):
                            idx += 1
                        attr_dict[attr_name] = enum_or_meta
                    # cell array of values
                    elif self._tk_eq(idx, (Token.Punctuation, '{')):
                        idx += 1
                        # closing curly braces terminate cell array
                        while self._tk_ne(idx, (Token.Punctuation, '}')):
                            idx += self._blanks(idx)  # skip blanks
                            # concatenate attr value string
                            attr_val = ''
                            # TODO: use _blanks or _indent instead
                            while (self._tk_ne(idx, (Token.Text, ' ')) and
                                   self._tk_ne(idx, (Token.Text, '\t')) and
                                   self._tk_ne(idx, (Token.Punctuation, ','))):
                                attr_val += self.tokens[idx][1]
                                idx += 1
                            idx += 1
                            if attr_val:
                                attr_dict[attr_name].append(attr_val)
                        idx += 1
                    idx += self._blanks(idx)  # skip blanks
                    # continue to next attribute separated by commas
                    if self._tk_eq(idx, (Token.Punctuation, ',')):
                        idx += 1
            idx += 1  # end of class attributes
        return attr_dict, idx

    def parse_group_header_comment(self, idx):
        group_name = ''
        group_docstr = ''
        # =====================================================================
        # docstring

        whitespace = self._whitespace(idx)
        idx += whitespace

        line = self.tokens[idx]

        if line[0] is Token.Comment:
            # group_name = line[1].lstrip('%')
            group_docstr = line[1].lstrip('%') + '\n'
            idx += 1
            idx += self._whitespace(idx)
            line = self.tokens[idx]
            while line and line[0] is Token.Comment:
                group_docstr += line[1].lstrip('%') + '\n'  # concatenate
                try:
                    idx += 1
                    idx += self._whitespace(idx)
                    line = self.tokens[idx]
                except IndexError:
                    break

        return (group_name, group_docstr, idx)

    @property
    def __module__(self):
        return self.module

    @property
    def __doc__(self):
        return unicode(self.docstring)

    @property
    def __bases__(self):
        bases_ = dict.fromkeys(self.bases)  # make copy of bases
        num_pths = len(MatObject.basedir.split(os.sep))
        # walk tree to find bases
        for root, dirs, files in os.walk(MatObject.basedir):
            # namespace defined by root, doesn't include basedir
            root_mod = '.'.join(root.split(os.sep)[num_pths:])
            # don't visit vcs directories
            for vcs in ['.git', '.hg', '.svn', '.bzr']:
                if vcs in dirs:
                    dirs.remove(vcs)
            # only visit mfiles
            for f in tuple(files):
                if not f.endswith('.m'):
                    files.remove(f)
            # search folders
            for b in self.bases:
                # search folders
                for m in dirs:
                    # check if module has been matlabified already
                    mod = sys.modules.get('.'.join([root_mod, m]).lstrip('.'))
                    if not mod:
                        continue
                    # check if base class is attr of module
                    b_ = mod.getter(b, None)
                    if b_:
                        bases_[b] = b_
                        break
                if bases_[b]:
                    continue
                if b + '.m' in files:
                    mfile = os.path.join(root, b) + '.m'
                    bases_[b] = MatObject.parse_mfile(mfile, b, root)
            # keep walking tree
        # no matching folders or mfiles
        return bases_

    def getter(self, name, *defargs):
        """
        :class:`MatClass` ``getter`` method to get attributes.
        """
        if name == '__name__':
            return self.__name__
        elif name == '__doc__':
            return self.__doc__
        elif name == '__module__':
            return self.__module__
        elif name == '__bases__':
            return self.__bases__
        elif name in self.properties:
            return self.properties[name]
        elif name in self.methods:
            return self.methods[name]
        elif name == '__dict__':
            objdict = OrderedDict([(pn, self.getter(pn)) for pn in
                            self.properties.iterkeys()])
            objdict.update(self.methods)
            return objdict
        else:
            super(MatClass, self).getter(name, *defargs)

class MatClassMemberGroup(MatObject):
    """Describes a properties or methods block in the code for the purposes of
    generating a header.
    """
    group_type = None
    group_title = None
    group_desc = None
    group_index = None

    # for properties
    dependent = False
    get_access = False
    set_access = False

    # for methods
    access = False
    static = False

    member_groups = None
    properties = None
    methods = None

    def __init__(self, name, cls, attrs, group_type, group_title, docstr, source_linestart):
        self.name = name
        self.cls = cls
        self.attrs = attrs
        self.docstring = docstr
        self.group_type = group_type
        self.group_title = group_title
        self.group_desc = ''

        self.methods = OrderedDict()
        self.properties = OrderedDict()
        self.member_groups = []

        self.source_linestart = source_linestart

        # construct group description
        attr = self.attrs
        if group_type == 'properties':
            if attr.has_key('GetAccess') and attr['GetAccess'] != 'public':
                self.get_access = False
            else:
                self.get_access = True
            if attr.has_key('SetAccess') and attr['SetAccess'] != 'public':
                self.set_access = False
            else:
                self.set_access = True
            self.dependent = attr.has_key('Dependent') and attr['Dependent']

            if self.get_access and not self.set_access:
                self.group_desc = 'Read-only Properties'
            elif self.set_access and not self.get_access:
                self.group_desc = 'Write-only Properties'
            else:
                self.group_desc = 'Properties'

            if self.dependent:
                self.group_desc = 'Dependent ' + self.group_desc

        elif group_type == 'methods':
            if attr.has_key('Access') and attr['Access'] != 'public':
                self.access = False
            else:
                self.access = True
            if attr.has_key('Static') and attr['Static']:
                self.static = True
            else:
                self.static = False
            if attr.has_key('Abstract') and attr['Abstract']:
                self.abstract = True
            else:
                self.abstract = False

            self.group_desc = 'Methods'
            if self.static:
                self.group_desc = 'Static ' + self.group_desc
            if self.abstract:
                self.group_desc = 'Abstract ' + self.group_desc

        elif group_type == 'enumeration':
            self.group_desc = 'Enumeration'

        else:
            raise Exception('Unknown group type')

    @property
    def __doc__(self):
        return unicode(self.docstring)

    def getter(self, name, *defargs):
        """
        :class:`MatClassMemberGroup` ``getter`` method to get attributes.
        """
        if name == '__name__':
            return self.__name__
        elif name == '__doc__':
            return self.__doc__
        elif name == '__module__':
            return self.__module__
        elif name == '__class__':
            return self.cls
        elif name in self.member_groups:
            return self.member_groups[name]
        elif name in self.properties:
            return self.properties[name]
        elif name in self.methods:
            return self.methods[name]
        elif name == '__dict__':
            objdict = OrderedDict([(pn, self.getter(pn)) for pn in
                                   self.properties.iterkeys()])
            objdict.update(self.methods)
            return objdict
        else:
            return None

class MatProperty(MatObject):
    def __init__(self, name, cls, attrs, default, docstring, source_linestart):
        super(MatProperty, self).__init__(name)
        self.cls = cls
        self.attrs = attrs
        self.default = default
        self.docstring = docstring

        self.source_linestart = source_linestart
        self.restriction_class = '' # proprety restricted to specific classes

    @property
    def __doc__(self):
        return unicode(self.docstring)


class MatMethod(MatFunction):
    def __init__(self, modname, tks, cls, attrs, linestart):
        # set name to None
        if attrs.has_key('Abstract') and attrs['Abstract']:
            abstract = True
        else:
            abstract = False

        super(MatMethod, self).__init__(None, modname, tks, linestart, abstract)
        self.cls = cls
        self.attrs = attrs
        self.is_getset = False

        self.source_linestart = linestart

        # skip first argument for class method
        if self.cls is not None and self.args is not None and not self.attrs.has_key('Static') and \
            self.cls.name != self.name: # constructor
            self.args = self.args[1:]

    def reset_tokens(self):
        num_rem_tks = len(self.rem_tks)
        len_meth = len(self.tokens) - num_rem_tks
        self.tokens = self.tokens[:-num_rem_tks]
        self.rem_tks = None
        return len_meth

    @property
    def __module__(self):
        return self.module

    @property
    def __doc__(self):
        return unicode(self.docstring)


class MatScript(MatObject):
    def __init__(self, name, path, tks, linenum_by_token):
        super(MatScript, self).__init__(name)
        self.path = path
        self.tks = tks
        self.docstring = ''
        self.linenum_by_token = linenum_by_token

    @property
    def __doc__(self):
        return unicode(self.docstring)


class MatException(MatObject):
    def __init__(self, name, path, tks):
        super(MatScript, self).__init__(name)
        self.path = path
        self.tks = tks
        self.docstring = ''

    @property
    def __doc__(self):
        return unicode(self.docstring)


class MatcodeError(Exception):
    def __str__(self):
        res = self.args[0]
        if len(self.args) > 1:
            res += ' (exception was: %r)' % self.args[1]
        return res


class MatModuleAnalyzer(object):
    # cache for analyzer objects -- caches both by module and file name
    cache = {}

    @classmethod
    def for_folder(cls, dirname, modname):
        if ('folder', dirname) in cls.cache:
            return cls.cache['folder', dirname]
        obj = cls(None, modname, dirname, True)
        cls.cache['folder', dirname] = obj
        return obj

    @classmethod
    def for_module(cls, modname):
        if ('module', modname) in cls.cache:
            entry = cls.cache['module', modname]
            if isinstance(entry, MatcodeError):
                raise entry
            return entry
        mod = sys.modules.get(modname)
        if mod:
            obj = cls.for_folder(mod.path, modname)
        else:
            err = MatcodeError('error importing %r' % modname)
            cls.cache['module', modname] = err
            raise err
        cls.cache['module', modname] = obj
        return obj

    def __init__(self, source, modname, srcname, decoded=False):
        # name of the module
        self.modname = modname
        # name of the source file
        self.srcname = srcname
        # file-like object yielding source lines
        self.source = source
        # cache the source code as well
        self.encoding = None
        self.code = None
        # will be filled by tokenize()
        self.tokens = None
        # will be filled by parse()
        self.parsetree = None
        # will be filled by find_attr_docs()
        self.attr_docs = None
        self.tagorder = None
        # will be filled by find_tags()
        self.tags = None

    def find_attr_docs(self, scope=''):
        """Find class and module-level attributes and their documentation."""
        if self.attr_docs is not None:
            return self.attr_docs
        attr_visitor_collected = {}
        attr_visitor_tagorder = {}
        tagnumber = 0
        mod = sys.modules[self.modname]
        # walk package tree
        for k, v in mod.safe_getmembers():
            if hasattr(v, 'docstring'):
                attr_visitor_collected[mod.package, k] = v.docstring
                attr_visitor_tagorder[k] = tagnumber
                tagnumber += 1
            if isinstance(v, MatClass):
                for mk, mv in v.getter('__dict__').iteritems():
                    namespace = '.'.join([mod.package, k])
                    attr_visitor_collected[namespace, mk] = mv.docstring
                    attr_visitor_tagorder[mk] = tagnumber
                    tagnumber += 1
        self.attr_docs = attr_visitor_collected
        self.tagorder = attr_visitor_tagorder
        return attr_visitor_collected
