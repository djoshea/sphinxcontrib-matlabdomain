This test case tests the use of multiple prefix characters in the
argparser.


------------


Command-line arguments
----------------------

Positional arguments
~~~~~~~~~~~~~~~~~~~~

    ============================================================================ ===========================================================================================================================================================
    *Option*                                                                     *Description*
    ---------------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------
    ``shortpos1``                                                                
    ``shortpos2``                                                                one-line help text
    ``shortpos3``                                                                this is very, very long help text which should span multiple lines and thus require special parsing. We'll also add `special` *chars* (default: 513251324)
    ``reallyreallyreallyreallyreallyreallyreallyreallylongpositionalargument1``  
    ``reallyreallyreallyreallyreallyreallyreallyreallylongpositionalargument2``   one-line help text
    ``reallyreallyreallyreallyreallyreallyreallyreallylongpositionalargument3``   this is very, very long help text which should span multiple lines and thus require special parsing. We'll also add `special` *chars* (default: 513251324)
    ============================================================================ ===========================================================================================================================================================


Optional arguments
~~~~~~~~~~~~~~~~~~

    ===================================================== ==========================================================================================================================================================
    *Option*                                              *Description*
    ----------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------
    ``-h``, ``--help``                                    show this help message and exit
    ``-a  X``                                             
    ``--bar  X``                                          one-line help text
    ``--c  X X``, ``--arg3  X X``                         this is very, very long help text which should span multiple lines and thus require special parsing. We'll also add `special` *chars* (default: 513251324)
    ``+x  X``                                             
    ``++another  ANOTHER``                                Another argument
    ``+y  ARG4 [ARG4 ...]``, ``++arg4  ARG4 [ARG4 ...]``   An argument beginning with '+'
    ===================================================== ==========================================================================================================================================================


------------


Script contents
---------------
