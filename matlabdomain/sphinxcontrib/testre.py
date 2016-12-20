import re

mat_ext_sig_re = re.compile(
r'''^(?:(\[?[\w\s,]+\]?)\s*=\s*)?   # return annotation
      ([+@]?[+@\w.]+::)?            # explicit module name
      ([+@]?[+@\w.]+\.)?            # module and/or class name(s)
      ([+@]?\w+)  \s*               # thing name
      (?: \((.*)\)                  # optional: arguments
      )? $                          # and nothing more
      ''', re.VERBOSE)

sig = '[int, hello] = addLabeledSpan([hello])'

match = mat_ext_sig_re.match(sig)
exmod, path, base, args, retann = match.groups()

print match.groups()

# ^(?:(\[?[a-z_,]+\]?)\s*=\s*)?([+@]?[+@\w.]+::)?([+@]?[+@\w.]+\.)?([+@]?\w+)\s*(?:\((.*)\))?$