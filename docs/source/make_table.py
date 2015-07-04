#!/usr/bin/env python
"""This script generates a two-column reStructuredText table in which:

  - each row corresponds to a module in a Python package

  - the first column points to the module documentation

  - the second column points to the module source code
"""
__date__   = "2015-07-4"
__author__ = "Joshua Griffin Dunn"
# coding": utf-8

import sys
import importlib
import argparse

from modulefinder import ModuleFinder

def get_submodules(package):
    """Find names of all modules in `package`

    Parameters
    ----------
    package : imported Python package


    Returns
    -------
    list
        List of module names as strings
    """
    mf = ModuleFinder()
    modules = ["%s.%s" % (package.__name__,X) for X in mf.find_all_submodules(package) if X != "__init__"]
    return modules

def get_link_pair(modname):
    """Return a link to the Sphinx documentation and source code for module specified by `modname`

    Parameters
    ----------
    modname : str
        Python module name, fully-qualified


    Returns
    -------
    str
        Link to module documentation

    str
        Link to module source code
    """
    slashname = modname.replace(".","/")
    p1 = ":mod:`~%s`" % modname
    p2 = "`%s <_modules/%s.html>`_" % (modname,slashname)
    #p2 = ":source:`%s.py`" % modname.replace(".","/")
    return p1, p2

def make_table(pairs,title=False):
    """Make a reStructuredText table from a list of pairs of items

    Parameters
    ----------
    pairs : list of tuples
        Paired values of columns 1 and 2

    title : bool, optional
        If `True`, the first pair is assumed to contain column headings
        (Default: `False1`)

    Returns
    -------
    str
        Multi-line reStructuredText table
    """
    col1, col2 = zip(*pairs)
    col1_len = 1 + max([len(X) for X in col1])
    col2_len = 1 + max([len(X) for X in col2])
    if title == True:
        col1_len += 4
        col2_len += 4

    header = ("="*col1_len) + "    " + ("="*col2_len) 
    template = "{0: <%ss}    {1: <%ss}" % (col1_len,col2_len)
    lines = [header]
    n = 0
    if title == True:
        lines.append(template.format("**%s**" % col1[0],"**%s**" % col2[0]))
        lines.append(header.replace("=","-"))
        n = 1

    for c1, c2 in zip(col1,col2)[n:]:
        lines.append(template.format(c1,c2))

    lines.append(header)
    return "\n".join(lines)


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("package",type=str,help="Python package to document")
    parser.add_argument("outfile",type=str,help="Output file")
    parser.add_argument("--title",default=[],nargs=2,
                        help="Column titles (optional)")

    args    = parser.parse_args(argv)


    print("Importing package '%s'..." % args.package)
    package = importlib.import_module(args.package)
    modules = get_submodules(package)
    print("Found %s submodules..." % len(modules))

    pairs = sorted([get_link_pair(X) for X in modules])
    title = False
    if len(args.title) > 0:
        print("Using column titles '%s' and '%s'" % (args.title[0],args.title[1]))
        title = True
        pairs = [tuple(args.title)] + pairs

    table = make_table(pairs,title=title)
    print("Writing to '%s'..." % args.outfile)
    with open(args.outfile,"w") as fout:
        fout.write(table)
        fout.write("\n")
        fout.close()

    print("Done.")

if __name__ == "__main__":
    main()
