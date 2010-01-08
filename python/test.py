#!/usr/bin/env python

# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@idiap.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

# import of standard modules
import sys
import os
from optparse import OptionParser

# third party modules
import cairo


# local modules


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


    import mypoppler
    mypoppler.init()
    filename = mypoppler.GooString('/tmp/558e56cb0bcb0de7c803d1d70b908088da019cf8a8760c1f0e2fee37.pdf')
    mypoppler.cvar.globalParams.setEnableFreeType("yes")
    mypoppler.cvar.globalParams.setAntialias("yes")
    mypoppler.cvar.globalParams.setVectorAntialias("yes")
    doc = mypoppler.PDFDoc(filename)
    splash = mypoppler.SplashOutputDev(mypoppler.splashModeRGB8, 3, False, (255, 255, 255))
    splash.startDoc(doc.getXRef())
    doc.displayPage(splash, 1, 300, 300, 0, True, False, False)
    bitmap = splash.getBitmap()
    data = bitmap.getDataPtr()
    import Image
    img = Image.fromstring('RGB', (bitmap.getWidth(), bitmap.getHeight()), data)
    img.save('/home/marietho/test.jpg')
    print bitmap
    filename.thisown = 0
