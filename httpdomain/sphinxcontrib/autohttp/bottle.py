"""
    sphinxcontrib.autohttp.bottle
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The sphinx.ext.autodoc-style HTTP API reference builder (from Bottle)
    for sphinxcontrib.httpdomain.

    :copyright: Copyright 2012 by Jameel Al-Aziz
    :license: BSD, see LICENSE for details.

"""

import re
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from docutils import nodes
from docutils.statemachine import ViewList

from sphinx.util import force_decode
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.util.docstrings import prepare_docstring
from sphinx.pycode import ModuleAnalyzer

from sphinxcontrib import httpdomain
from sphinxcontrib.autohttp.common import http_directive, import_object


def translate_bottle_rule(app, rule):
    buf = StringIO.StringIO()
    for name, filter, conf in app.router.parse_rule(rule):
        if filter:
            buf.write('(')
            buf.write(name)
            if filter != app.router.default_filter or conf:
                buf.write(':')
                buf.write(filter)
            if conf:
                buf.write(':')
                buf.write(conf)
            buf.write(')')
        else:
            buf.write(name)
    return buf.getvalue()


def get_routes(app):
    for rule, methods in app.router.rules.iteritems():
        for method, target in methods.iteritems():
            if method in ('OPTIONS', 'HEAD'):
                continue
            path = translate_bottle_rule(app, rule)
            yield method, path, target


class AutobottleDirective(Directive):

    has_content = True
    required_arguments = 1
    option_spec = {'endpoints': str,
                   'undoc-endpoints': str,
                   'include-empty-docstring': str}

    @property
    def endpoints(self):
        try:
            endpoints = re.split(r'\s*,\s*', self.options['endpoints'])
        except KeyError:
            # means 'endpoints' option was missing
            return None
        return frozenset(endpoints)

    @property
    def undoc_endpoints(self):
        try:
            endpoints = re.split(r'\s*,\s*', self.options['undoc-endpoints'])
        except KeyError:
            return frozenset()
        return frozenset(endpoints)

    def make_rst(self):
        app = import_object(self.arguments[0])
        for method, path, target in get_routes(app):
            endpoint = target.name or target.callback.__name__
            if self.endpoints and endpoint not in self.endpoints:
                continue
            if endpoint in self.undoc_endpoints:
                continue
            view = target.callback
            docstring = view.__doc__ or ''
            if not isinstance(docstring, unicode):
                analyzer = ModuleAnalyzer.for_module(view.__module__)
                docstring = force_decode(docstring, analyzer.encoding)
            if not docstring and 'include-empty-docstring' not in self.options:
                continue
            docstring = prepare_docstring(docstring)
            for line in http_directive(method, path, docstring):
                yield line

    def run(self):
        node = nodes.section()
        node.document = self.state.document
        result = ViewList()
        for line in self.make_rst():
            result.append(line, '<autobottle>')
        nested_parse_with_titles(self.state, result, node)
        return node.children


def setup(app):
    if 'http' not in app.domains:
        httpdomain.setup(app)
    app.add_directive('autobottle', AutobottleDirective)

