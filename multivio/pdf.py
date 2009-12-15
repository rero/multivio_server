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
import gfx

from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from pdfminer.cmap import CMapDB, find_cmap_path
# third party modules


# local modules
class PdfError:
    class InvalidUrl(Exception):
        pass

class PdfConverter:
    def __init__(self):
        pass
    
    def getPng(self, url, pagenr=1, zoom=1.0):
        (filename, headers) = urllib.urlretrieve(url)
        doc = gfx.open("pdf", filename)
        page = doc.getPage(pagenr)
        width = int(page.width * zoom)
        height = int(page.height * zoom)
        data = page.asImage(width, height)
        img = Image.fromstring('RGB', (width, height), data)
        f = cStringIO.StringIO()
        img.save(f, "PNG")
        f.seek(0)
        content = f.read()
        header = [('content-type', 'image/png'), ('content-length',
        str(len(content)))]
        #output to browser
        return(header, content)

    def getHtml(self, url, zoom=1.0, pagenr=1):
        (filename, headers) = urllib.urlretrieve(url)
        infp = file(filename, 'r')
        codec = 'utf-8'
        maxpages=10
        maxfilesize=5000000
        html=True
        outfp = cStringIO.StringIO()
        cmapdir = find_cmap_path()
        cmapdb = CMapDB(cmapdir)
        rsrc = PDFResourceManager(cmapdb)
        laparams = LAParams()
        if html:
            device = HTMLConverter(rsrc, outfp, codec=codec, laparams=laparams,
                scale=zoom, showpageno=False,pagepad=0)
        else:
            device = TextConverter(rsrc, outfp, codec=codec, laparams=laparams)
        process_pdf(rsrc, device, infp, [pagenr-1], maxpages=maxpages)
        outfp.seek(0)
        header = [('content-type', 'text/html')]
        content = outfp.read()
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


