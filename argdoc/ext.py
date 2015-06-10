#!/usr/bin/env python
'''
Created on Jun 9, 2015

@author: joshua
'''
import re
import shlex
import subprocess


_SUBCOMMAND_HEADER = "%sSubcommand arguments\n%s--------------------\n"

_REQUIRED = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]
"""Extensions required by :py:obj:`argdoc`"""


patterns = { "section_title"      : r"^(\w+.*):$",
             "opt_only"           : r"^  (-?[^\s]+(,\s--[^\s]+)?)$",
             "opt_plus_args"      : r"^  (-+[^\s]+(,\s--[^\s]+\s[^\s]+)?)(\s[^\s]+)+$",
             "opt_plus_desc"      : r"^  (?P<left>-?[^\s]+(,\s--[^\s]+)?)\s\s+(?P<right>.*)",
             "opt_plus_args_desc" : r"^  (?P<left>-+[^\s]+(,\s--[^\s]+(\s[^\s])+)?(\s\w+)+)\s\s+(?P<right>.*)$",             
             #"opt_plus_args_desc" : r"^  (?P<left>-+[^\s]+(,\s--[^\s]+)?(\s\w+)+)\s\s+(?P<right>.*)$",
             "continue_desc"      : r"^ {24}(.*)",
             "section_desc"       : r"^ (\s[^- ]+)+$",
             "subcommands"        : r"^subcommands:$",
             "subcommand_names"   : r"^  {((?:\w+)(?:(?:,(?:\w+))+)?)}$"             
            }
"""Regular expressions describing components of docstrings created by :py:mod:`argparse`"""

patterns = { K : re.compile(V) for K,V in patterns.items() }  

def noargdoc(func):
    """Decorator that forces argdoc to skip processing of `func` 
    
    Parameters
    ----------
    func : function
        `main` function of a command-line module
    
    Returns
    -------
    func
        wrapped function
    """
    func.__dict__["noargdoc"] = True
    return func

def get_subcommand_header(name,indent_size=4):
    return "%s .. Rubric:: %s" % (indent_size,name)

def process_subprogram_container(app,obj,help_lines,start_line,indent_size=4,section_head=False):
    """Processes help output from an :py:class:`argparse.ArgumentParser`
    of subprograms, or of a program that has no subprograms
    
    Parameters
    ----------
    app
        Sphinx application
            
    obj : module
        Module containing `main` function
            
    help_lines : list
        List of strings, each corresponding to a line of output from
        ``some_script --help``
    
    start_line : int
        Line where token `'subcommands: '` was found in argparser output
    
    indent_size : int, optional
        Number of spaces to prepend before output. This is significant,
        because whitespace is significant in reStructuredText, and 
        incorrect indentation size will muddle the rendering. (Default: 4)
    
    section_head : bool, optional
        If True, a section header for "Command-line arguments" will be included.
        This messes up parsing for function docstrings, but is fine for module
        docstrings (Default: False).
    
    Returns
    -------
    list
        List of strings encoding reStructuredText table of command-line arguments
    """
    out_lines = (_SUBCOMMAND_HEADER % (indent_size,indent_size)).split("\n")
    for line in help_lines[start_line+1:]:
        match = patterns["subcommand_names"].search(line.strip("\n")) 
        if match is not None:
            subcommands = match.groups()[0].split(",")
            break
    
    # FIXME
    print(subcommands)
    for subcommand in subcommands:
        out_lines.append(get_subcommand_header(subcommand,indent_size=indent_size))
        call = shlex.split("python %s %s --help" % (obj.__name__,subcommand))
        try:
            proc = subprocess.Popen(call,stdout=subprocess.PIPE)
            sub_help_lines = proc.communicate()[0].split("\n")
            out_lines.extend(process_single_or_sub_program(app,
                                                           obj,
                                                           sub_help_lines,
                                                           indent_size=indent_size,
                                                           section_head=section_head))            
        except subprocess.CalledProcessError as e:
            out  = ("-"*75) + "\n" + e.output + "\n" + ("-"*75)
            out += "Could not call module %s as '%s'. Output:\n"% (obj.__name__, e.cmd)
            out += e.output
            out += ("-"*75) + "\n"
            app.warn(out)

    return out_lines

def process_single_or_sub_program(app,obj,help_lines,indent_size=4,section_head=False):
    """Processes help output from an :py:class:`argparse.ArgumentParser`
    of subprograms, or of a program that has no subprograms
    
    Parameters
    ----------
    app
        Sphinx application
        
    obj : module
        Module containing `main` function
            
    help_lines : list
        List of strings, each corresponding to a line of output from
        ``some_script --help``
    
    indent_size : int, optional
        Number of spaces to prepend before output. This is significant,
        because whitespace is significant in reStructuredText, and 
        incorrect indentation size will muddle the rendering. (Default: 4)
    
    section_head : bool, optional
        If True, a section header for "Command-line arguments" will be included.
        This messes up parsing for function docstrings, but is fine for module
        docstrings (Default: False).
    
    Returns
    -------
    list
        List of strings encoding reStructuredText table of command-line arguments
    """
    started = False

    out_lines = []
    col1      = []
    col2      = []
    section_title = []
    section_desc  = []
    
    for line in help_lines:
        line = line.rstrip()
        if len(line.strip()) == 0 and started == True:
            # close table and write out previous section
            if len(col1) > 0 and len(col2) > 0:
                col1_width = 1 + max([len(X) for X in col1]) + 4
                col2_width = max([len(X) for X in col2])
                out_lines.append("")
                out_lines.append("")
                out_lines.extend(section_title)
                out_lines.extend(section_desc)
                out_lines.append("")
                out_lines.append( (" "*indent_size)+("="*col1_width) + " " + ("="*col2_width))# + "\n" )
                out_lines.append( (" "*indent_size)+"*Option*" + " "*(1 + col1_width - 8) + "*Description*")# + "\n" )
                out_lines.append( (" "*indent_size)+("="*col1_width) + " " + ("="*col2_width))# + "\n" )
                 
                for c1, c2 in zip(col1,col2):
                    out_lines.append((" "*indent_size)+ "``" + c1 + "``" + (" "*(1+col1_width-len(c1))) + c2)# + "\n" )
     
                out_lines.append( (" "*indent_size)+("="*col1_width) + " " + ("="*col2_width))#  + "\n"  )
                out_lines.append("")
                
                section_title = []
                section_desc  = []
                col1 = []
                col2 = []
            
        #elif patterns["section_title"].search(line) is not None and not line.startswith("usage:"):
        #FIXME: this is a kludge to deal with __doc__ lines that have trailing colons
        elif line.startswith("positional arguments:") or line.startswith("optional arguments:"):
            
            if started == False:
                started = True
                if section_head == True:
                    out_lines.append(" "*indent_size + "Command-line arguments")
                    out_lines.append(" "*indent_size + "----------------------")
            
            # start section
            match = patterns["section_title"].search(line)
            
            section_title = ["%s%s" % (" "*indent_size,match.groups()[0].capitalize()),
                             "%s%s" % (" "*indent_size,("."*len(match.groups()[0]))),
                            ]
        elif patterns["section_title"].search(line) is not None and not line.startswith("usage:"):
            match = patterns["section_title"].search(line)
            
            section_title = ["%s%s" % (" "*indent_size,match.groups()[0].capitalize()),
                             "%s%s" % (" "*indent_size,("."*len(match.groups()[0]))),
                            ]
        elif patterns["section_desc"].search(line) is not None and started == True:
            section_desc.append(line.strip())
            
        elif patterns["opt_only"].search(line) is not None and started == True:
            col1.append(line.strip())
            col2.append("")
        elif patterns["opt_plus_args"].search(line) is not None and started == True:
            col1.append(line.strip())
            col2.append("")
        elif patterns["continue_desc"].search(line) is not None and started == True:
            col2[-1] += line.strip("\n")
        elif patterns["opt_plus_desc"].search(line) is not None and started == True:
            match = patterns["opt_plus_desc"].search(line).groupdict()
            #assert len(col1) == len(col2)
            col1.append(match["left"])
            col2.append(match["right"])
        elif patterns["opt_plus_args_desc"].search(line) is not None and started == True:
            match = patterns["opt_plus_args_desc"].search(line).groupdict()
            col1.append(match["left"])
            col2.append(match["right"])
    
    return out_lines

def process_argparser_help(app,obj,help_lines,indent_size=4,section_head=False):
    """Processes help output from an :py:class:`argparse.ArgumentParser`
    into a set of reStructuredText tables, probing subparsers as needed.
    
    Parameters
    ----------
    app
        Sphinx application
    
    obj : module
        Module containing `main` function
    
    help_lines : list
        List of strings, each corresponding to a line of output from
        ``some_script --help``
    
    indent_size : int, optional
        Number of spaces to prepend before output. This is significant,
        because whitespace is significant in reStructuredText, and 
        incorrect indentation size will muddle the rendering. (Default: 4)
    
    section_head : bool, optional
        If True, a section header for "Command-line arguments" will be included.
        This messes up parsing for function docstrings, but is fine for module
        docstrings (Default: False).
    
    Returns
    -------
    list
        List of strings corresponding to reStructuredText table
    """
    for n,line in enumerate(help_lines):
        if patterns["subcommands"].match(line.strip("\n")) is not None:
            out_lines = process_subprogram_container(app,obj,help_lines,n,
                                                     indent_size=indent_size,
                                                     section_head=section_head)
        else:
            out_lines = process_single_or_sub_program(app,obj,help_lines,
                                                      indent_size=indent_size,
                                                      section_head=section_head)                                  

    return out_lines

def add_args_to_module_docstring(app,what,name,obj,options,lines):
    """Insert a table describing command-line parameters into the documentation
    for the `main` method of a command-line script. `main` methods decorated 
    with the :func:`noargdoc` decorator will be skipped.
    
    Notes
    -----
    Per the Sphinx spec, this function modifies `lines` in place.
    
    This will only work for command-line scripts using :py:mod:`argparse`
    
    
    Parameters
    ----------
    app
        Sphinx application
    
    what : str
        Type of object (e.g. "module", "function", "class")
    
    name : str
        Fully-qualified name of object
    
    obj : object
        Object to skip or not
    
    options : object
        Options given to the directive, whose boolean properties are set to True
        if their corresponding flag was given in the directive

    lines : list
        List of strings the docstrings, after Sphinx processing
    """
    if what == "module" and obj.__dict__.get("main",None) is not None:
        if obj.__dict__.get("main").__dict__.get("noargdoc",False) == False:
            call = shlex.split("python %s --help" % obj.__name__)
            try:
                proc = subprocess.Popen(call,stdout=subprocess.PIPE)
                help_lines = proc.communicate()[0].split("\n")
            except subprocess.CalledProcessError as e:
                out  = ("-"*75) + "\n" + e.output + "\n" + ("-"*75)
                out += "Could not call module %s as '%s'. Output:\n"% (obj.__name__, e.cmd)
                out += e.output
                out += ("-"*75) + "\n"
                app.warn(out)
            try:
                out_lines = process_argparser_help(app,obj,help_lines,indent_size=0,section_head=True)
                lines.extend(out_lines)
            except IndexError as e:
                app.warn("Error processing argparser into docstring for module %s: " % obj.__name__)

def setup(app):
    """Set up :obj:`argdoc` extension and register with `Sphinx`_
    
    Parameters
    ----------
    app
        Sphinx application
    """    
    for ext in _REQUIRED:
        app.setup_extension(ext)
    
    app.connect("autodoc-process-docstring",add_args_to_module_docstring)