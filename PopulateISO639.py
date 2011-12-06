# -*- coding: utf-8 -*-
"""
Tags ISO-639 language codes in FluidInfo.

Iterates over the listing of ISO 639 codes supplied by the 
US american "Library of Congress" at:
    http://www.loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt
    
... and puts the following tags on
FluidInfo objects of (duck)type "ISO 639 code":

    fluiddb/about
        string, 2 or 3 letters
        Plain ISO 639 code in lower case.

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


"""


import sys
import os.path
import urllib
import urllib2

from fom.session import Fluid
from fom.mapping import Namespace, Tag
    

urlISOcodeListing = "http://www.loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt"


def AddTag(dictTags, sTagPath, TagValue):
    """
        Add a tag to a dict that conforms to the structure required by FluidInfo.values.put API call.
    """
    dictTags[unicode(sTagPath)] = {u'value': TagValue}

    
def ImportISO639(sLine, dictObjects):
    # Get rid of end of line character.
    sLine = sLine.strip()
    
    # Delimiter for fields is |
    # Delimiter for subfields is ;
    llFields = [sField.split(u';') for sField in sLine.split(u'|')]
    
    # Replace Fields which are a list with a single empty string item with None value
    # Also strip whitespace, since semicolon delimiter is often followed by a space.
    # Doing this in ugly C style, since I don't know how to do that the Python way.
    llTmp = []
    for Field in llFields:
        Field = [SubField.strip() for SubField in Field]    # strips whitespace from subfield items
        if len(Field)==1 and Field[0]=='':
            llTmp.append(None)
        else:
            llTmp.append(Field)
            
    llFields = llTmp
    
    ###############################
    # 1st field: ISO639-2/B code.
    #              If the second field is empty, then this is also a ISO639-2/T code.
    #
    # 2nd field: ISO639-2/T code or None if T code is equal to B code.
    #
    # 3rd field: ISO639-1 code or None if there's no equivalent.
    #
    # 4th field: English glossonym
    #
    # 5th field: French glossonym
    
    
    
    ##################################
    # Populating FluidInfo object
    # corresponding to ISO639-2 code
    
    assert(llFields[0] is not None)
    assert(len(llFields[0]) == 1)
    
    
    sAbout2 = llFields[0][0]
    
    # Stip any occurence of the unicode Byte Order Mark
    #   The http://loc.gov reply contains one of those as first character.
    #   See: http://en.wikipedia.org/wiki/Byte_Order_Mark
    sAbout2 = sAbout2.strip(u'\ufeff')
    
    if len(sAbout2) != 3:
        print "Skipping malformed record:", llFields
        return
        
    assert(sAbout2.islower())
    assert(sAbout2.isalpha())
    
    # DEBUGGING: Skip anything other than eng and spa, to avoid trashing FluidInfo if anything goes wrong.
    #if (sAbout2 not in [u'eng', u'spa']):
    #    return
    
    
    print "Importing:", sAbout2
    dictObjects[sAbout2] = dict()
    
    AddTag(dictObjects[sAbout2], sUserNS+'/lang/iso639/2', None)
    AddTag(dictObjects[sAbout2], sUserNS+'/lang/iso639/2B', None)
    
    # This is *also* a valid ISO639-2/T code, if the second field is empty!
    if llFields[1] is None:
        AddTag(dictObjects[sAbout2], sUserNS+'/lang/iso639/2T', None)
        
    # English glossonym
    if llFields[3] is not None:
        AddTag(dictObjects[sAbout2], sUserNS+'/lang/glossonym/eng', llFields[3][0])
        AddTag(dictObjects[sAbout2], sUserNS+'/lang/glossonym/eng-all', llFields[3])
        
    # French glossonym
    if llFields[4] is not None:
        AddTag(dictObjects[sAbout2], sUserNS+'/lang/glossonym/fra', llFields[4][0])
        AddTag(dictObjects[sAbout2], sUserNS+'/lang/glossonym/fra-all', llFields[4])
    
    if llFields[2] is not None:
        ##################################
        # Populating FluidInfo object
        # corresponding to ISO639-1 code
        assert(len(llFields[0]) == 1)
        
        sAbout1 = llFields[2][0]
        
        assert(len(sAbout1)==2)
        
        dictObjects[sAbout1] = dict()
        AddTag(dictObjects[sAbout1], sUserNS+'/lang/iso639/1', None)
        # Linking ISO639-1 to ISO639-2 code
        AddTag(dictObjects[sAbout1], sUserNS+'/lang/iso639/related-2', sAbout2)
        
        # Linking ISO639-2 to ISO639-1 code
        AddTag(dictObjects[sAbout2], sUserNS+'/lang/iso639/related-1', sAbout1)
        
        # English glossonym
        if llFields[3] is not None:
            AddTag(dictObjects[sAbout1], sUserNS+'/lang/glossonym/eng', llFields[3][0])
            AddTag(dictObjects[sAbout1], sUserNS+'/lang/glossonym/eng-all', llFields[3])
            
        # French glossonym
        if llFields[4] is not None:
            AddTag(dictObjects[sAbout1], sUserNS+'/lang/glossonym/fra', llFields[4][0])
            AddTag(dictObjects[sAbout1], sUserNS+'/lang/glossonym/fra-all', llFields[4])
            
        
def CommitTagging(dictObjects):
    """
        Iterates over the dictionary containing the tags to be put on objects
        and commits it via FluidInfo value.put API calls.
    """
    for sAbout, dictTags in dictObjects.items():
        print "Commiting:",sAbout
        fdb.values.put( query='fluiddb/about = "'+sAbout+'"',values=dictTags)
    
    
if __name__ == "__main__":

    #############################
    # Bind to FluidInfo instance
    fileCredentials = open(os.path.expanduser('~/.fluidDBcredentials'), 'r')
    username = fileCredentials.readline().strip()
    password = fileCredentials.readline().strip()
    fileCredentials.close()
    # fdb = Fluid('https://sandbox.fluidinfo.com')  # The sandbox instance
    fdb = Fluid()  # The main instance
    fdb.login(username, password)
    fdb.bind()
    nsUser = Namespace(username)
    
    sUserNS = nsUser.path     # Ugly use of a global, I know. :-)
    
    dictObjects = dict()
    
    fRequest = urllib2.urlopen(urlISOcodeListing)

    # Get enconding of listing.
    # This should usually be UTF-8, but it could change and cause a big headache!
    # sEncoding = fRequest.headers['content-type'].split('charset=')[-1]
    # ^^^^This is not working, since http://loc.org is not specifying the encoding. Dammit!
    #      fRequest.headers['content-type'] = 'text/plain'
    #        instead of:
    #      fRequest.headers['content-type'] = 'text/html; charset=windows-1251'
    # So we hardcode it:
    sEncoding = "utf-8"
    
    
    while 1:
        
        sLine = fRequest.readline()
        
        if not sLine:
            break
        
        # Convert into full-fledged unicode.
        # This is also necessary for UTF-8 !
        sLine = unicode(sLine, sEncoding)
        
        ImportISO639(sLine,dictObjects)
    
    # import pprint
    # pprint.pprint(dictObjects )
    
    CommitTagging(dictObjects)
    
    
    # Put some usefull info on the description-tag of the namespace objects.
    Namespace(sUserNS+u'/lang')._set_description( u'Data imported by the fiLang scripts found at https://github.com/axeloide/fiLang')
    Namespace(sUserNS+u'/lang/iso639')._set_description( u'Data related to ISO 639 language codes.')
    Namespace(sUserNS+u'/lang/glossonym')._set_description( u'Contains language names.')
    
    Tag(sUserNS+u'/lang/iso639/1')._set_description( u'Flags valid ISO639-1 language codes. Empty-valued.')
    Tag(sUserNS+u'/lang/iso639/2')._set_description( u'Flags valid ISO639-2 language codes. Empty-valued.')
    Tag(sUserNS+u'/lang/iso639/2B')._set_description( u'Flags valid ISO639-2/B language codes. Empty-valued.')
    Tag(sUserNS+u'/lang/iso639/2T')._set_description( u'Flags valid ISO639-2/T language codes. Empty-valued.')
    
    for sTagPath in Namespace(sUserNS+u'/lang/glossonym').tag_paths:
        sCode = sTagPath.split(u'/')[-1]
        Tag(sTagPath)._set_description( u'A language as named in '+sCode)

