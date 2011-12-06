fiLang
==========
Tools to populate FluidInfo with language data.

Yet another testbench for @axeloide's thoughts about leveraging FluidInfo to get
difficult data into a more usable representation.


Base namespace is: ./lang  (relative to user namespace)


PopulateISO639.py
-----------------

Tags ISO-639 language codes in FluidInfo.

Iterates over the listing of ISO 639 codes supplied by the 
US american "Library of Congress" at:
    http://www.loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt
    
... and puts the following tags on
FluidInfo objects of (duck)type "ISO 639 code":

    fluiddb/about
        string, 2 or 3 letters
        Plain ISO 639-1 or ISO 639-2 code in lower case.

    ./lang/iso639/1 
        empty-valued
        Indicates that the fluiddb/about value is a valid ISO 639-1 code.
        
    ./lang/iso639/2
        empty-valued
        Indicates that the fluiddb/about value is a valid ISO 639-2 code.
        Flags both: B and T codes
        See: http://en.wikipedia.org/wiki/ISO_639-2
    
    ./lang/iso639/2T
        empty-valued
        Indicates that the fluiddb/about value is a valid ISO 639-2/T code.
        See: http://en.wikipedia.org/wiki/ISO_639-2#B_and_T_codes
        
    ./lang/iso639/2B
        empty-valued
        Indicates that the fluiddb/about value is a valid ISO 639-2/B code
        See: http://en.wikipedia.org/wiki/ISO_639-2#B_and_T_codes        
        
    ./lang/iso639/related-1
        string, 2-letters
        Contains the equivalent ISO 639-1 code.
        Not tagged if the object is a ISO 639-1 code itself.

    ./lang/iso639/related-2
        string, 3-letters
        Contains the equivalent ISO 639-2 code.
        Not tagged if the object is a ISO 639-2 or ISO 639-3 code itself.
        
    ./lang/glossonym/<xxx>
        string, possibly containing some of the wildest unicode characters around.
        Where <xxx> stands for a three-letter ISO639-2/T code.
        Contains the preferred name of the language in language xxx.
        This program will only populate this for 
            xxx=eng=english
            xxx=fra=français
        Other glossonyms to be populated by other programs, e.g. via Wikipedia API
        
    ./lang/glossonym/<xxx>-all
        set of strings, possibly containing some of the wildest unicode characters around.
        Where <xxx> stands for a three-letter ISO639-2/T code.
        Contains all of the names of the language in language xxx, since there
        are some cases where there are alternative namings. 
        Example:
            fluiddb/about = "es"
            ./lang/glossonym/eng-all = ["Spanish" , "Castilian"]
            
        This program will only populate this for 
            xxx=eng=english
            xxx=fra=français


This is kind of the core tool, since other scripts will later iterate over
those FluidInfo objects to perform other tasks.




ToDo
----    
* Error checking, error checking, error checking!
  Everything is currently coded in a "blindly optimistic" way.
  A HowTo on error checking urllib2 calls:
    + http://docs.python.org/howto/urllib2.html
  
* Include a timestamp tag like "./lang/iso639/timestamp-lastupdate"


Ideas for future tools
----------------------

* Add tagging for ISO 639-3 and ISO 639-5
    ./lang/iso639/3
        empty-valued
        Indicates that the fluiddb/about value is a valid ISO 639-3 code
        Not a superset of ISO639-2 because it omits language colection codes.
        See: http://en.wikipedia.org/wiki/ISO_639-3
        

    ./lang/iso639/related-3
        string, 3-letters
        Contains the equivalent ISO 639-3 code.
        Not tagged if the object is a ISO 639-3 code itself.


* Tag a url to the Wikipedia project authored in that language
    ./lang/related-wikipedia
        string
        Contains the base-url to the Wikipedia project authored in that language.
        Not tagged if the object is a ISO 639-3 code itself.
  
* Tag more glossonyms.
    ./lang/glossonym/<xxx>
    ./lang/glossonym/<xxx>-all
  
  Use Wikipedia API to get some mappings:
   + http://www.mediawiki.org/wiki/API:Query_-_Properties#langlinks_.2F_ll
     Examples:
        For a given article, get alternative languages:
        http://en.wikipedia.org/w/api.php?action=query&titles=Spanish&prop=langlinks&lllimit=200&format=xml
        
        Get a list of all language-ids and autoglossonyms:
        http://en.wikipedia.org/w/api.php?action=query&meta=siteinfo&siprop=languages
        
        

Pointers to stuff
-----------------

Other registration-authorities or listings:
    http://www.sil.org/iso639-3/codes.asp
    
    http://www.loc.gov/standards/iso639-2/php/English_list.php
    http://www.loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt
    
    http://www.loc.gov/standards/iso639-5/iso639-5.pipe.txt
    http://www.loc.gov/standards/iso639-5/iso639-5.skos.rdf
    
    http://www.iana.org/assignments/language-subtag-registry
    
