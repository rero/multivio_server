#!/usr/bin/env python

# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

# import of standard modules
import sys
import os
import Image
import cStringIO
from optparse import OptionParser
import urllib

# third party modules


# local modules
class ThumbError:
    class InvalidUrl(Exception):
        pass

class Thumb:
    def __init__(self):
        pass
    
    def generate(self, url, size=100):
        print '------->',url, size
        size = int(size)
        image_file = urllib.urlopen(url)
        im = cStringIO.StringIO(image_file.read()) # constructs a StringIO holding the image
        img = Image.open(im)
        print '------->',img.format, img.size, img.mode
        img.thumbnail((size, size), Image.ANTIALIAS)
        print '------->',img.format, img.size, img.mode
        #del img
        #write to file object
        f = cStringIO.StringIO()
        img.save(f, "PNG")
        #img.save('out.jpg')
        f.seek(0)
        content = f.read()
        header = [('content-type', 'image/png'), ('content-length',
        str(len(content)))]
        #output to browser
        return(header, content)



#---------------------------- Main Part ---------------------------------------

if __name__ == '__main__':

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("Change It")



    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)


    (options,args) = parser.parse_args ()

    if len(args) != 0:
        parser.error("Error: incorrect number of arguments, try --help")


