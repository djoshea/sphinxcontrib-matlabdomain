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


------------


Command-line arguments
----------------------

Positional arguments
~~~~~~~~~~~~~~~~~~~~

    ============================================================================ ================================================================================================================================================================================================================================
    *Option*                                                                     *Description*
    ---------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    ``shortpos1``                                                                
    ``shortpos2``                                                                one-line help text
    ``shortpos3``                                                                this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``reallyreallyreallyreallyreallyreallyreallyreallylongpositionalargument1``  
    ``reallyreallyreallyreallyreallyreallyreallyreallylongpositionalargument2``                          one-line help text
    ``reallyreallyreallyreallyreallyreallyreallyreallylongpositionalargument3``                          this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ============================================================================ ================================================================================================================================================================================================================================


Optional arguments
~~~~~~~~~~~~~~~~~~

    =========================================================================================================== ================================================================================================================================================================================================================================
    *Option*                                                                                                    *Description*
    ----------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    ``-h``, ``--help``                                                                                          show this help message and exit
    ``-a  X``                                                                                                   
    ``-b  X``                                                                                                   one-line help text
    ``-c  X``                                                                                                   this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--double1  X``                                                                                            
    ``--double2  X``                                                                                            one-line help text
    ``--double3  X``                                                                                            this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-d  X``, ``--combo1  X``                                                                                  
    ``-e  X``, ``--combo2  X``                                                                                  one-line help text
    ``-f  X``, ``--combo3  X``                                                                                  this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--reallyreallyreallyreallyreallyreallylong_double1  X``                                                   
    ``--reallyreallyreallyreallyreallyreallylong_double2  X``                                                                           one-line help text
    ``--reallyreallyreallyreallyreallyreallylong_double3  X``                                                                           this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-g  X``, ``--reallyreallyreallyreallyreallyreallylong_combo1  X``                                         
    ``-i  X``, ``--reallyreallyreallyreallyreallyreallylong_combo2  X``                                                                 one-line help text
    ``-j  X``, ``--reallyreallyreallyreallyreallyreallylong_combo3  X``                                                                 this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-k  X X``                                                                                                 
    ``-l  X X``                                                                                                 one-line help text
    ``-m  X X``                                                                                                 this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--double4  X X``                                                                                          
    ``--double5  X X``                                                                                          one-line help text
    ``--double6  X X``                                                                                          this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-n  X X``, ``--combo4  X X``                                                                              
    ``-o  X X``, ``--combo5  X X``                                                                              one-line help text
    ``-p  X X``, ``--combo6  X X``                                                                              this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--reallyreallyreallyreallyreallyreallylong_double4  X X``                                                 
    ``--reallyreallyreallyreallyreallyreallylong_double5  X X``                                                                         one-line help text
    ``--reallyreallyreallyreallyreallyreallylong_double6  X X``                                                                         this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-q  X X``, ``--reallyreallyreallyreallyreallyreallylong_combo4  X X``                                     
    ``-r  X X``, ``--reallyreallyreallyreallyreallyreallylong_combo5  X X``                                                             one-line help text
    ``-s  X X``, ``--reallyreallyreallyreallyreallyreallylong_combo6  X X``                                                             this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-t  X [X ...]``                                                                                           
    ``-u  X [X ...]``                                                                                           one-line help text
    ``-v  X [X ...]``                                                                                           this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--double7  X [X ...]``                                                                                    
    ``--double8  X [X ...]``                                                                                    one-line help text
    ``--double9  X [X ...]``                                                                                    this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-w  X [X ...]``, ``--combo7  X [X ...]``                                                                  
    ``-x  X [X ...]``, ``--combo8  X [X ...]``                                                                                          one-line help text
    ``-y  X [X ...]``, ``--combo9  X [X ...]``                                                                                          this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--reallyreallyreallyreallyreallyreallylong_double7  X [X ...]``                                           
    ``--reallyreallyreallyreallyreallyreallylong_double8  X [X ...]``                                                                   one-line help text
    ``--reallyreallyreallyreallyreallyreallylong_double9  X [X ...]``                                                                   this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-z  X [X ...]``, ``--reallyreallyreallyreallyreallyreallylong_combo7  X [X ...]``                         
    ``-A  X [X ...]``, ``--reallyreallyreallyreallyreallyreallylong_combo8  X [X ...]``                                                 one-line help text
    ``-B  X [X ...]``, ``--reallyreallyreallyreallyreallyreallylong_combo9  X [X ...]``                                                 this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-C  [X]``                                                                                                 
    ``-D  [X]``                                                                                                 one-line help text
    ``-E  [X]``                                                                                                 this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--double10  [X]``                                                                                         
    ``--double11  [X]``                                                                                         one-line help text
    ``--double12  [X]``                                                                                         this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-F  [X]``, ``--combo10  [X]``                                                                             
    ``-G  [X]``, ``--combo11  [X]``                                                                                                     one-line help text
    ``-H  [X]``, ``--combo12  [X]``                                                                                                     this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--reallyreallyreallyreallyreallyreallylong_double10  [X]``                                                
    ``--reallyreallyreallyreallyreallyreallylong_double11  [X]``                                                                        one-line help text
    ``--reallyreallyreallyreallyreallyreallylong_double12  [X]``                                                                        this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-I  [X]``, ``--reallyreallyreallyreallyreallyreallylong_combo10  [X]``                                    
    ``-J  [X]``, ``--reallyreallyreallyreallyreallyreallylong_combo11  [X]``                                                            one-line help text
    ``-K  [X]``, ``--reallyreallyreallyreallyreallyreallylong_combo12  [X]``                                                            this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-L  [X [X ...]]``                                                                                         
    ``-M  [X [X ...]]``                                                                                         one-line help text
    ``-N  [X [X ...]]``                                                                                         this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--double13  [X [X ...]]``                                                                                 
    ``--double14  [X [X ...]]``                                                                                                         one-line help text
    ``--double15  [X [X ...]]``                                                                                                         this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-O  [X [X ...]]``, ``--combo13  [X [X ...]]``                                                             
    ``-P  [X [X ...]]``, ``--combo14  [X [X ...]]``                                                                                     one-line help text
    ``-Q  [X [X ...]]``, ``--combo15  [X [X ...]]``                                                                                     this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--reallyreallyreallyreallyreallyreallylong_double13  [X [X ...]]``                                        
    ``--reallyreallyreallyreallyreallyreallylong_double14  [X [X ...]]``                                                                one-line help text
    ``--reallyreallyreallyreallyreallyreallylong_double15  [X [X ...]]``                                                                this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-R  [X [X ...]]``, ``--reallyreallyreallyreallyreallyreallylong_combo13  [X [X ...]]``                    
    ``-S  [X [X ...]]``, ``--reallyreallyreallyreallyreallyreallylong_combo14  [X [X ...]]``                                            one-line help text
    ``-T  [X [X ...]]``, ``--reallyreallyreallyreallyreallyreallylong_combo15  [X [X ...]]``                                            this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-U  {one_choice}``                                                                                        
    ``-V  {one_choice}``                                                                                        one-line help text
    ``-W  {one_choice}``                                                                                        this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--double16  {one_choice}``                                                                                
    ``--double17  {one_choice}``                                                                                                        one-line help text
    ``--double18  {one_choice}``                                                                                                        this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-X  {one_choice}``, ``--combo16  {one_choice}``                                                           
    ``-Y  {one_choice}``, ``--combo17  {one_choice}``                                                                                   one-line help text
    ``-Z  {one_choice}``, ``--combo18  {one_choice}``                                                                                   this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--reallyreallyreallyreallyreallyreallylong_double16  {one_choice}``                                       
    ``--reallyreallyreallyreallyreallyreallylong_double17  {one_choice}``                                                               one-line help text
    ``--reallyreallyreallyreallyreallyreallylong_double18  {one_choice}``                                                               this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-1  {one_choice}``, ``--reallyreallyreallyreallyreallyreallylong_combo16  {one_choice}``                  
    ``-2  {one_choice}``, ``--reallyreallyreallyreallyreallyreallylong_combo17  {one_choice}``                                          one-line help text
    ``-3  {one_choice}``, ``--reallyreallyreallyreallyreallyreallylong_combo18  {one_choice}``                                          this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-4  {one,two,three,four}``                                                                                
    ``-5  {one,two,three,four}``                                                                                                        one-line help text
    ``-6  {one,two,three,four}``                                                                                                        this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--double19  {one,two,three,four}``                                                                        
    ``--double20  {one,two,three,four}``                                                                                                one-line help text
    ``--double21  {one,two,three,four}``                                                                                                this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-7  {one,two,three,four}``, ``--combo19  {one,two,three,four}``                                           
    ``-8  {one,two,three,four}``, ``--combo20  {one,two,three,four}``                                                                   one-line help text
    ``-9  {one,two,three,four}``, ``--combo21  {one,two,three,four}``                                                                   this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``--reallyreallyreallyreallyreallyreallylong_double19  {one,two,three,four}``                               
    ``--reallyreallyreallyreallyreallyreallylong_double20  {one,two,three,four}``                                                       one-line help text
    ``--reallyreallyreallyreallyreallyreallylong_double21  {one,two,three,four}``                                                       this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    ``-Â  {one,two,three,four}``, ``--reallyreallyreallyreallyreallyreallylong_combo19  {one,two,three,four}``  
    ``-Ã  {one,two,three,four}``, ``--reallyreallyreallyreallyreallyreallylong_combo20  {one,two,three,four}``                          one-line help text
    ``-Ä  {one,two,three,four}``, ``--reallyreallyreallyreallyreallyreallylong_combo21  {one,two,three,four}``                          this is very, very long help text which should span                        multiple lines and thus require special parsing. We'll                        also add `special` *chars* (default: 513251324)
    =========================================================================================================== ================================================================================================================================================================================================================================


------------


Script contents
---------------
