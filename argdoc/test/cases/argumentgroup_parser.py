#!/usr/bin/env python
"""This test case tests the processing of argument groups with short,
long, or no description. Argument groups should be styled as paragraph-
level sections, with their descriptions appearing below the title,
followed by the options.

-------------------

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean feugiat
tempor diam sed condimentum. Mauris aliquam interdum libero, ut aliquet
erat malesuada sed. Mauris nec venenatis sapien, a feugiat neque. Sed
pulvinar erat sit amet posuere aliquet. Phasellus non quam tincidunt,
semper velit vitae, eleifend ante. Nam finibus vulputate diam. Fusce sit
amet leo aliquam magna gravida fringilla et eu justo. Pellentesque vulputate
elit id dignissim vehicula. Sed tempor interdum lacus, in dapibus magna
interdum eu. Fusce lacinia turpis vel risus porta, eget dapibus nisi
eleifend. Maecenas dictum nec nisi sit amet dignissim. Duis vestibulum
ipsum a vestibulum placerat. Vestibulum ante ipsum primis in faucibus orci
luctus et ultrices posuere cubilia Curae; Nullam consequat nulla quis quam
interdum, eu auctor ante molestie.

Cum sociis natoque penatibus et magnis dis parturient montes, nascetur
ridiculus mus. Ut egestas nec leo a luctus. Suspendisse libero magna,
ultricies vel porttitor varius, vulputate nec orci. Ut et vehicula neque.
Quisque ut libero eget sem pretium mollis elementum vitae quam. Etiam varius
rutrum iaculis. Mauris consectetur cursus dolor nec tincidunt. Morbi aliquam
elit ipsum, at aliquam purus ultricies sed. Donec tortor ante, consectetur
et faucibus non, dignissim vitae eros. Duis pharetra convallis efficitur.
Curabitur congue in tortor luctus molestie. Donec turpis felis, sollicitudin
volutpat tristique quis, mattis at arcu. Praesent interdum luctus sodales.
Sed imperdiet augue vulputate hendrerit tincidunt. Curabitur pharetra, odio
in laoreet pretium, metus turpis posuere dui, quis aliquet leo nisl
sollicitudin ligula.

Here is a table, to show that we can have rich formatting:

    =============  ======================================================
    **Column 1**   **Column 2**
    -------------  ------------------------------------------------------
     Some item     Some other item.

     Table row 2.  Table row 2 column 2.

     Another row.  Row with a link to `Python <https://www.python.org>`_
    =============  ======================================================
 

See also
--------
A definition list
    The purpose of this `See also` section is just to show that we can use
    a number of reStructuredText structures, and still have the argument
    descriptions appended below.

Here is another item
    To show that our test works
"""
import argparse
import sys

g1_title = "One group of arguments"
g1_description = """Sometimes it is useful to group arguments that relate to each other in
an argument group. This can make command-line help, documentation, and source
code more intelligible to others"""

g2_title = "A second group of arguments"
g2_description = "Description of second argument group"

g3_title = "A final group of arguments, with no description"

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("mainarg1")
    parser.add_argument("mainarg2",help="main positional argument #2")
        
    g1 = parser.add_argument_group(title=g1_title,description=g1_description)
    g2 = parser.add_argument_group(title=g2_title,description=g2_description)
    g3 = parser.add_argument_group(title=g3_title)

    g1.add_argument("fooarg1",help="foo argument 1")
    g1.add_argument("fooarg2",help="foo argument 2")
    g1.add_argument("-f",help="short foo argument",type=str)
    g1.add_argument("--fookwarg",help="foo keyword argument",type=str)
    g1.add_argument("-v","--verbose",help="foo verbosely")    

    g2.add_argument("bararg",help="bar argument")
    g2.add_argument("--choice",choices=("option1","option2","option3"),
                           help="A keyword that requries a choice")
    
    g3.add_argument("bazarg",help="baz argument")
    g3.add_argument("--numbers",metavar="M",nargs=3,help="numerical argument")
    g3.add_argument("-z","--zoom",help="zzzzzzzzzzzzzz")
     
    args   = parser.parse_args(argv)

if __name__ == "__main__":
    main()
