# -*- coding: utf-8 -*-
"""
Adds some glossonyms to FluidInfo objects for ISO-639 language codes.

Processes info obtained from Wikipedia API with:
http://en.wikipedia.org/w/api.php?action=query&meta=siteinfo&siprop=interwikimapformat=xml

    NOTE: Above API call seems more appropriate to extract endonyms than this:
        http://en.wikipedia.org/w/api.php?action=query&meta=siteinfo&siprop=languages
        ... which has many additional remarks in parenthesis and uses script suffixes.


    NOTE: Requesting XML, since it is quite easier to process thanks to XPath.
    
Updates the following tags on
FluidInfo objects of (duck)type "ISO 639 code":

    ./lang/glossonym/<xxx>
        string, possibly containing some of the wildest unicode characters around.
        Where <xxx> stands for a two or three-letter ISO639 code.
        Contains the preferred name of the language in language xxx.
        
    ./lang/glossonym/<xxx>-all
        set of strings, possibly containing some of the wildest unicode characters around.
        Where <xxx> stands for a three-letter ISO639-2/T code.
        Contains all of the names of the language in language xxx, since there
        are some cases where there are alternative namings. 
        
    ./lang/glossonym/_all
        set of strings, possibly containing some of the wildest unicode characters around.
        Contains all of the names of the language in all languages.
        NOTE: TagName is prefixed with underscore to avoid clash with any potential "all" language code!!
        All names converted to lowercase, to avoid ambiguity, since we want to use this as
        a way to lookup: [glossonym in any language] ---> [language-code]
        Example:
            fluiddb/about = "es"
            ./lang/glossonym/_all = ["spanish" , "castilian", "espagnol", "castillan", "spanisch", "castellà", ...]

"""


import sys
import os.path
import urllib
import urllib2

import json    

from fom.session import Fluid
from fom.mapping import Object, Namespace, Tag
    

urlWikipediaAPI = "http://en.wikipedia.org/w/api.php"


def GetInterwikimap():
    """
    http://en.wikipedia.org/w/api.php?action=query&meta=siteinfo&siprop=interwikimap&format=json
    """
    # Request Interwikimap
    data = urllib.urlencode({ 'action': 'query'
                             ,'meta'  : 'siteinfo'
                             ,'siprop': 'interwikimap'
                             ,'format': 'json'})
    # print data
    jReply = json.load(urllib2.urlopen(urlWikipediaAPI, data ))
    # tree.write(sys.stdout)
    
    dictIW = dict()
    
    # Match all map entries with a language attribute.
    for jInterWikiItem in jReply["query"]["interwikimap"]:
        if 'language' in jInterWikiItem:
            sPrefix = jInterWikiItem['prefix']
            dictIW[sPrefix] = jInterWikiItem
            # Split language values containing a forward slash, which seem to denote spelling in alternative scripts.
            dictIW[sPrefix]['language'] = [sSpell.strip() for sSpell in dictIW[sPrefix]['language'].split('/')]
            
    
    return dictIW




def AddTag(dictTags, sTagPath, TagValue):
    """
        Add a tag to a dict that conforms to the structure required by FluidInfo.values.put API call.
    """
    dictTags[unicode(sTagPath)] = {u'value': TagValue}

                
        
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
    
    ldIWM = GetInterwikimap()
    
    for sIwmPrefix, dIWM in ldIWM.items():    
        Response = fdb.values.get(query=u'fluiddb/about="'+sIwmPrefix+'" AND (HAS '+sUserNS+u'/lang/iso639/1 OR HAS '+sUserNS+u'/lang/iso639/2)', taglist=[sUserNS+'/lang/iso639/related-2B', sUserNS+'/lang/iso639/related-2T'])
        assert(Response.status == 200)
        assert(Response.content_type == 'application/json')
        dQueryMatch = json.loads(Response.content)["results"]

        if len(dQueryMatch.values()[0]) == 0:
            print "No match for InterwikiMap prefix: ", sIwmPrefix, "   (Probably a missing ISO639-3 code, or a suffixed composite code.)"
        else:
            sBcode = dQueryMatch.values()[0].values()[0].values()[0].values()[0]
            sTcode = dQueryMatch.values()[0].values()[0].values()[1].values()[0]
            sWikiHome = dIWM['url'].rstrip(u'$1')
            print "InterwikiMap prefix: ", sIwmPrefix, "---> ISO639-2 B/T =", sBcode, sTcode, "  WikiHome: ", sWikiHome
            lsAutoglossonyms = dIWM['language']
            ##
            if sIwmPrefix not in dictObjects.keys():
                dictObjects[sIwmPrefix] = dict()
            AddTag(dictObjects[sIwmPrefix], sUserNS+u'/lang/glossonym/'+sIwmPrefix, lsAutoglossonyms[0])
            AddTag(dictObjects[sIwmPrefix], sUserNS+u'/lang/glossonym/'+sBcode, lsAutoglossonyms[0])
            AddTag(dictObjects[sIwmPrefix], sUserNS+u'/lang/glossonym/'+sTcode, lsAutoglossonyms[0])
            AddTag(dictObjects[sIwmPrefix], sUserNS+u'/lang/glossonym/autoglossonym', lsAutoglossonyms[0])
            AddTag(dictObjects[sIwmPrefix], sUserNS+u'/lang/glossonym/'+sIwmPrefix+u'-all', lsAutoglossonyms)
            AddTag(dictObjects[sIwmPrefix], sUserNS+u'/lang/glossonym/'+sBcode+u'-all', lsAutoglossonyms)
            AddTag(dictObjects[sIwmPrefix], sUserNS+u'/lang/glossonym/'+sTcode+u'-all', lsAutoglossonyms)
            AddTag(dictObjects[sIwmPrefix], sUserNS+u'/lang/glossonym/autoglossonym-all', lsAutoglossonyms)
            AddTag(dictObjects[sIwmPrefix], sUserNS+u'/lang/wikipedia-home', sWikiHome)
            ##
            if sBcode not in dictObjects.keys():
                dictObjects[sBcode] = dict()
            AddTag(dictObjects[sBcode], sUserNS+u'/lang/glossonym/'+sIwmPrefix, lsAutoglossonyms[0])
            AddTag(dictObjects[sBcode], sUserNS+u'/lang/glossonym/'+sBcode, lsAutoglossonyms[0])
            AddTag(dictObjects[sBcode], sUserNS+u'/lang/glossonym/'+sTcode, lsAutoglossonyms[0])
            AddTag(dictObjects[sBcode], sUserNS+u'/lang/glossonym/autoglossonym', lsAutoglossonyms[0])
            AddTag(dictObjects[sBcode], sUserNS+u'/lang/glossonym/'+sIwmPrefix+u'-all', lsAutoglossonyms)
            AddTag(dictObjects[sBcode], sUserNS+u'/lang/glossonym/'+sBcode+u'-all', lsAutoglossonyms)
            AddTag(dictObjects[sBcode], sUserNS+u'/lang/glossonym/'+sTcode+u'-all', lsAutoglossonyms)
            AddTag(dictObjects[sBcode], sUserNS+u'/lang/glossonym/autoglossonym-all', lsAutoglossonyms)
            AddTag(dictObjects[sBcode], sUserNS+u'/lang/wikipedia-home', sWikiHome)
            ##
            if sTcode not in dictObjects.keys():
                dictObjects[sTcode] = dict()
            AddTag(dictObjects[sTcode], sUserNS+u'/lang/glossonym/'+sIwmPrefix, lsAutoglossonyms[0])
            AddTag(dictObjects[sTcode], sUserNS+u'/lang/glossonym/'+sBcode, lsAutoglossonyms[0])
            AddTag(dictObjects[sTcode], sUserNS+u'/lang/glossonym/'+sTcode, lsAutoglossonyms[0])
            AddTag(dictObjects[sTcode], sUserNS+u'/lang/glossonym/autoglossonym', lsAutoglossonyms[0])
            AddTag(dictObjects[sTcode], sUserNS+u'/lang/glossonym/'+sIwmPrefix+u'-all', lsAutoglossonyms)
            AddTag(dictObjects[sTcode], sUserNS+u'/lang/glossonym/'+sBcode+u'-all', lsAutoglossonyms)
            AddTag(dictObjects[sTcode], sUserNS+u'/lang/glossonym/'+sTcode+u'-all', lsAutoglossonyms)
            AddTag(dictObjects[sTcode], sUserNS+u'/lang/glossonym/autoglossonym-all', lsAutoglossonyms)
            AddTag(dictObjects[sTcode], sUserNS+u'/lang/wikipedia-home', sWikiHome)
            

    import pprint
    pprint.pprint(dictObjects)
    
    print "############### Going to tag:", len(dictObjects), "objects###############"
    
    CommitTagging(dictObjects)
    
        
    # Put some usefull info on the description-tag of the tag objects.
    Tag(sUserNS+u'/lang/wikipedia-home')._set_description( u'Base URL of Wikipedia project authored in that language.')
    Tag(sUserNS+u'/lang/glossonym/autoglossonym')._set_description( u'Name of a language in that very same language.')
    Tag(sUserNS+u'/lang/glossonym/autoglossonym-all')._set_description( u'List of names of a language in that very same language.')
    
    Tag(sUserNS+u'/lang/iso639/related-1')._set_description( u'Link to corresponding ISO 639-1 code.')
    Tag(sUserNS+u'/lang/iso639/related-2B')._set_description( u'Link to corresponding ISO 639-2/B code.')
    Tag(sUserNS+u'/lang/iso639/related-2T')._set_description( u'Link to corresponding ISO 639-2/T code.')

    
    #for sTagPath in Namespace(sUserNS+u'/lang/glossonym').tag_paths:
    #    sCode = sTagPath.split(u'/')[-1]
    #    Tag(sTagPath)._set_description( u'A language as named in '+sCode)

