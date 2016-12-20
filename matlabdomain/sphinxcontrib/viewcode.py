# -*- coding: utf-8 -*-
"""
    sphinx.ext.viewcode
    ~~~~~~~~~~~~~~~~~~~

    Add links to module code in Python object descriptions.

    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import traceback

import sys
from six import iteritems, text_type
from docutils import nodes

import sphinx
from sphinx import addnodes
from sphinx.locale import _
from sphinx.pycode import ModuleAnalyzer
from sphinx.util import get_full_modname
from sphinx.util.nodes import make_refnode
from sphinx.util.console import blue

from mat_types import MatModuleAnalyzer

# def _get_full_modname(app, modname, attribute):
#     try:
#         module = sys.modules[modname]
#
#         # Allow an attribute to have multiple parts and incidentially allow
#         # repeated .s in the attribute.
#         value = module
#         for attr in attribute.split('.'):
#             if attr:
#                 value = value.getter(attr)
#
#         return value.__module__
#
#     except AttributeError:
#         # sphinx.ext.viewcode can't follow class instance attribute
#         # then AttributeError logging output only verbose mode.
#         app.verbose('Didn\'t find %s in %s' % (attribute, modname))
#         return None
#     except Exception as e:
#         # sphinx.ext.viewcode follow python domain directives.
#         # because of that, if there are no real modules exists that specified
#         # by py:function or other directives, viewcode emits a lot of warnings.
#         # It should be displayed only verbose mode.
#         app.verbose(traceback.format_exc().rstrip())
#         app.verbose('viewcode can\'t import %s, failed with error "%s"' %
#                     (modname, e))
#         return None


def get_object(app, modname, entry):
    """Find an object in the docstrings"""
    module = sys.modules[modname]

    # Allow an attribute to have multiple parts and incidentially allow
    # repeated .s in the attribute.
    value = module
    for attr in entry.split('.'):
        if attr:
            value = value.getter(attr)

    return value

def doctree_read(app, doctree):
    env = app.builder.env
    # if not hasattr(env, '_viewcode_mat_code'):
    env._viewcode_mat_code= {}
    # if not hasattr(env, '_viewcode_mat_lineref'):
    env._viewcode_mat_lineref = {}

    if app.builder.name == "singlehtml":
        return
    if app.builder.name.startswith("epub") and not env.config.viewcode_enable_epub:
        return

    for objnode in doctree.traverse(addnodes.desc):
        if objnode.get('domain') != 'mat':
            continue
        names = set()
        for signode in objnode:
            if not isinstance(signode, addnodes.desc_signature):
                continue
            modname = signode.get('module')
            fullname = signode.get('fullname')
            tokens = fullname.split('.')
            clsname = tokens[0]
            if len(tokens) > 1:
                member_name = tokens[1]
            else:
                member_name = ''

            # refname = modname + '_' + clsname
            # if env.config.viewcode_import:
            #     modname = _get_full_modname(app, modname, fullname)
            if not modname:
                continue
            # fullname = signode.get('fullname')
            # if not has_tag(modname, fullname, env.docname, refname):
            #     continue
            if fullname in names:
                # only one link per name, please
                continue
            names.add(fullname)
            # one page per class
            pagename = '_code/' + modname.replace('.', '/') + '/' + clsname
            onlynode = addnodes.only(expr='html')
            onlynode += addnodes.pending_xref(
                '', reftype='viewcode', refdomain='std', refexplicit=False,
                reftarget=pagename, refid=fullname,
                refdoc=env.docname)
            onlynode[0] += nodes.inline('', _('[source]'),
                                        classes=['viewcode-link'])
            signode += onlynode

            classkey = modname + ':' + clsname

            matobj = get_object(app, modname, fullname)
            if matobj is None:
                continue

            # if class, store code if not already stored
            if not env._viewcode_mat_code.has_key(classkey):
                mat_class = get_object(app, modname, clsname)
                if mat_class is not None:
                    env._viewcode_mat_code[classkey] = mat_class.code

            # mark the start line of code for this entry in the lookup table
            if not env._viewcode_mat_lineref.has_key(classkey):
                env._viewcode_mat_lineref[classkey] = {}

            print "%s :: %s : %s at line %d, from %s" % (modname, clsname, fullname, matobj.source_linestart, matobj.docname)
            env._viewcode_mat_lineref[classkey][matobj.source_linestart] = (modname, clsname, fullname, matobj.docname)

def env_merge_info(app, env, docnames, other):
    if hasattr(other, '_viewcode_mat_lineref'):
        if not hasattr(env, '_viewcode_mat_lineref'):
            env._viewcode_mat_lineref = {}
        # now merge in the information from the subprocess
        env._viewcode_mat_lineref.update(other._viewcode_mat_lineref)

    if hasattr(other, '_viewcode_mat_code'):
        if not hasattr(env, '_viewcode_mat_code'):
            env._viewcode_mat_code = {}
        # now merge in the information from the subprocess
        env._viewcode_mat_code.update(other._viewcode_mat_code)


def missing_reference(app, env, node, contnode):
    # resolve our "viewcode" reference nodes -- they need special treatment
    if node['reftype'] == 'viewcode':
        return make_refnode(app.builder, node['refdoc'], node['reftarget'],
                            node['refid'], contnode)

def collect_pages(app):
    env = app.builder.env
    if not hasattr(env, '_viewcode_mat_code'):
        return
    highlighter = app.builder.highlighter
    urito = app.builder.get_relative_uri

#    app.builder.info(' (%d module code pages)' %
#                     len(env._viewcode_modules), nonl=1)

    pagename_lookup = {}
    fullname_lookup = {}

    for classkey, linenum_starts in app.status_iterator(
            iteritems(env._viewcode_mat_code), 'highlighting module code... ',
            blue, len(env._viewcode_mat_code), lambda x: x[0]):
        if not linenum_starts:
            continue

        modname, clsname = classkey.split(':')

        # construct a page name for the highlighted source
        pagename = '_code/' + modname.replace('.', '/') + '/' + clsname

        # cache the pagename for later
        pagename_lookup[classkey] = pagename

        # generate the Matlab proper name
        parentModules = [x for x in modname.split('.') if x.startswith('+')]
        full_classname = '.'.join(parentModules) + '.' + clsname
        fullname_lookup[classkey] = full_classname

        code = env._viewcode_mat_code[classkey]

        # highlight the source using the builder's highlighter
        lexer = 'matlab'
        highlighted = highlighter.highlight_block(code, lexer, linenos=True)
        # split the code into lines
        lines = highlighted.splitlines()

        # find first line of code
        before1, before2, codelines = highlighted.split('<pre>', 2)

        # nothing to do for the last line; it always starts with </pre> anyway
        # now that we have code lines (starting at index 1), insert anchors for
        # the collected tags (HACK: this only works if the tag boundaries are
        # properly nested!)

        lines_with_ref = env._viewcode_mat_lineref[classkey]
        codelines = codelines.splitlines()

        for start, refinfo in iteritems(lines_with_ref):
            modname = refinfo[0]
            fullname = refinfo[2]
            docname = refinfo[3]
            backlink = urito(pagename, docname) + '#' + modname.replace('/', '.') + '.' + fullname
            codelines[start-1] = (
                '<a name="%s"></a>'
                '<a class="viewcode-back" style="background-color: white; padding-left: 0; z-index: 1000; position: relative;"'
                'href="%s">%s</a>' % (fullname, backlink, _('[docs]')) +
                codelines[start-1])
            # lines[min(end - 1, maxindex)] += '</div>'
        # try to find parents (for submodules)

        parents = []
        parent = modname
        while '.' in parent:
            parent = parent.rsplit('.', 1)[0]
            # if parent in modnames:
            parents.append({
                'link': urito(pagename, '_code/' +
                              parent.replace('.', '/')),
                'title': parent})
        parents.append({'link': urito(pagename, '_code/index'),
                        'title': _('Module code')})
        parents.reverse()
        # putting it all together
        lines = before1 + '<pre>' + before2 + '<pre style="max-width: 680px; overflow-x: scroll;">' + '\n'.join(codelines)
        context = {
            'parents': parents,
            'title': clsname,
            'body': (_('<h1>Source code for %s</h1>') % full_classname +
                     lines),
        }

        yield (pagename, context, 'page.html')

    code_files = env._viewcode_mat_code

    html = ['\n']
    # the stack logic is needed for using nested lists for submodules
    stack = ['']
    classkeys = env._viewcode_mat_code
    for classkey in sorted(classkeys):
        modname, clsname = classkey.split(':')
        pagename = pagename_lookup[classkey]
        fullname = fullname_lookup[classkey]

        if modname.startswith(stack[-1]):
            stack.append(modname + '.')
            html.append('<ul>')
        else:
            stack.pop()
            while not modname.startswith(stack[-1]):
                stack.pop()
                html.append('</ul>')
            stack.append(modname + '.')
        html.append('<li><a href="%s">%s</a></li>\n' % (
            urito('_code/index', pagename),
            fullname))
    html.append('</ul>' * (len(stack) - 1))
    context = {
        'title': _('Overview: module code'),
        'body': (_('<h1>All modules for which code is available</h1>') +
                 ''.join(html)),
    }

    yield ('_code/index', context, 'page.html')

# setup integrated with matlab.py's setup

# def setup(app):
#     app.add_config_value('viewcode_import', True, False)
#     app.add_config_value('viewcode_enable_epub', False, False)
#     app.connect('doctree-read', doctree_read)
#     app.connect('env-merge-info', env_merge_info)
#     app.connect('html-collect-pages', collect_pages)
#     app.connect('missing-reference', missing_reference)
#     # app.add_config_value('viewcode_include_modules', [], 'env')
#     # app.add_config_value('viewcode_exclude_modules', [], 'env')
#     return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
