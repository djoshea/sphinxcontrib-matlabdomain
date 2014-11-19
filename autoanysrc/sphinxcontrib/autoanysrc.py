# -*- coding: utf-8 -*-
import os
import glob
import codecs

from sphinx.util.console import bold
from sphinx.ext.autodoc import Documenter


class AnySrcDocumenter(Documenter):
    """
    Specialized Documenter subclass for any source files
    """
    objtype = 'anysrc'
    content_indent = u''
    titles_allowed = True

    # proxy directive paramenters only
    option_spec = {
        'src': lambda x: x,
        'analyzer': lambda x: x,
    }

    analyzer_by_key = {}

    @classmethod
    def register_analyzer(cls, key, analyzer_class):
        """Register analyzer

        :param domain: one of sphinx domain (js, c, cpp, etc.)
        :param anaylyzer_class: subclass of BaseAnalyzer
        """
        cls.analyzer_by_key[key] = analyzer_class

    def info(self, msg):
        self.directive.env.app.info('    <autoanysrc> %s' % msg)

    def collect_files(self):
        arg = self.options.src
        if arg is None:
            return []
        if not os.path.isabs(arg):
            arg = os.path.join(
                self.directive.env.srcdir,
                arg,
            )
        self.info('collect by: ' + bold(arg))
        return glob.glob(arg)

    def process(self):
        """process files one by one with analyzer"""

        for filepath in self.collect_files():

            self.info('processing: ' + bold(filepath))
            self.directive.env.note_dependency(filepath)

            with codecs.open(filepath, 'r', 'utf-8') as f:
                content = f.read()

            for line, lineno in self.analyzer.process(content):
                self.add_line(line, filepath, lineno)

    def generate(
            self, more_content=None, real_modname=None,
            check_module=False, all_members=False):

        # initialize analyzer
        analyzer_class = self.analyzer_by_key.get(self.options.analyzer)
        if not analyzer_class:
            self.info(
                'Analyzer not defined for: %s' % self.options.anaylyzer
            )
            return
        self.analyzer = analyzer_class(self)

        # start generate docs
        self.add_line('', '<autoanysrc>')

        # set default domain if it specified in anaylyzer instance
        if hasattr(self.analyzer, 'domain'):
            self.add_line(
                '.. default-domain:: %s' % self.analyzer.domain, '<autoanysrc>'
            )
            self.add_line('', '<autoanysrc>')

        # inject docs from sources
        self.process()


def setup(app):

    # register default anaylzers
    from .analyzers import JSAnalyzer
    AnySrcDocumenter.register_analyzer('js', JSAnalyzer)

    app.add_autodocumenter(AnySrcDocumenter)

    return {'version': '0.0.0', 'parallel_read_safe': True}
