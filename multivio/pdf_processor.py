#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Document Parser module for Multivio"""

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules ---------------------------------------

# import of standard modules
import cStringIO
import sys

# local modules
from processor import DocumentProcessor
import poppler
from web_app import ApplicationError

#----------------------------------- Exceptions --------------------------------

#----------------------------------- Classes -----------------------------------

#_______________________________________________________________________________
class PdfProcessor(DocumentProcessor):
    """Class to process pdf document"""
#_______________________________________________________________________________
    def __init__(self, file_name):
        DocumentProcessor.__init__(self, file_name)
        poppler.cvar.globalParams.setEnableFreeType("yes")
        poppler.cvar.globalParams.setAntialias("yes")
        poppler.cvar.globalParams.setVectorAntialias("yes")
        self._doc = poppler.PDFDoc(self._file_name)

    def _check(self):
        """Check if the document is valid."""
        return True

    def render(self, max_output_size=None, angle=0, index=None,
        output_format=None):
        """Render the document content.

            max_output_size -- tupple: maximum dimension of the output
            angle -- int: angle in degree
            index -- dict: index in the document
            output_format -- string: select the output format
            
        return:
            mime_type -- string: output mime type
            data -- string: output data
        """
        self.logger.debug("Render")
        return self._get_image_from_pdf(page_nr=index['page_number'],
            max_width=max_output_size[0], max_height=max_output_size[1],
            angle=angle, output_format=output_format)
    
    def get_size(self, index=None):
        """Return the size of the document content.
            index -- dict: index in the document
            
        return:
            data -- string: output data
        """
        page_nr = index['page_number']
        size = {}
        size['width'] = self._doc.getPageMediaWidth(page_nr)
        size['height'] = self._doc.getPageMediaHeight(page_nr)

        return size

    def search(self, query, from_=None, to_=None, max_results=None, sort=None):
        """Search parts of the document that match the given query.

            from_ -- dict: start the search at from_
            to_ -- dict: end the search at to_
            max_results -- int: limit the number of the returned results
            sort -- string: sort the results given the sort criterion
        return:
            a dictionary with the founded results
        """    
        # number of results
        num_results = 0

        # number of pages in document
        num_pages = self._doc.getNumPages()        

        print "%d pages detected" % num_pages
    
        # conversion of text to search to unicode
        query = unicode(query.decode('utf-8'))

        ## findText options: perform find from top to bottom of page
        startAtTop = True
        stopAtBottom = True
        startAtLast = False
        stopAtLast = False
        caseSensitive = False
        backward = False

        # param check TODO report errors
        if (from_ is None): from_ = 1
        if (to_ is None): to_ = num_pages + 1   
        if (max_results in [0, None]): max_results = sys.maxint

        # calculate page range [1, num_pages+1]
        (from_, to_) = (max(from_, 1), min(to_ + 1, num_pages + 1))

        # results for the current file
        result = {
          'context': 'text',
          'file_position': {
            'url':'TODO://%s' % self._file_name,
            'results':[ # results for that file go here
            ] 
          }
        }

        # current result
        cur_res = {}

        # note: to_ is not included in range
        done = False
        for np in range(from_, to_):
            # debug
            print "searching on page %d" % np

            if done is True:
                break

            td = poppler.TextOutputDev(None, True, False, False)
            self._doc.displayPage(td, np, 72, 72, 0, True, True, False)
            text_page = td.takeText()
            (found, x1, y1, x2, y2) = text_page.findText(query, startAtTop, stopAtBottom, startAtLast, stopAtLast, caseSensitive, backward)
        
            ## findText options: find from last find to bottom of page
            startAtTop = False
            stopAtBottom = True 
            startAtLast = True
  
            while found is True:
                #print "%s word found at page %s, bbx: (%s, %s, %s, %s)" % (query, np, x1, y1, x2, y2)
                # build structure for the found word
                cur_res = {
                  'preview': 'TODO: %s'%query,
                  'index': {
                    'page': np, 
                    'bounding_box': {'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2}
                  }
                }
                
                # append result to list
                result['file_position']['results'].append(cur_res)
                                
                num_results = num_results + 1
                if (num_results >= max_results):
                    done = True
                    break
                # find additional words on page
                (found, x1, y1, x2, y2) = text_page.findText(query, startAtTop, stopAtBottom, startAtLast, stopAtLast, caseSensitive, backward)

        return result

    def indexing(self, output_file):
        """Batch indexing of the document.
        return:
            True if everything is ok.
        """
        return None

    def _get_optimal_scale(self, max_width, max_height, page_nr):
        """Compute the optimal scale factor."""
        if max_width is None and max_height is None:
            return 1.0
        page_width = self._doc.getPageMediaWidth(page_nr)
        page_height = self._doc.getPageMediaHeight(page_nr)
        page_ratio = page_height/float(page_width)
        if max_width is None:
            max_width = max_height/page_ratio
        if max_height is None:
            max_height = max_width*page_ratio
        scale = max_width/page_width
        if max_height < (page_height*scale):
            scale = max_height/page_height
        return scale

    def _get_image_from_pdf(self, page_nr=1, max_width=None, max_height=None,
        angle=0, output_format='JPEG'):
        """Render a pdf page as image."""
        if self._doc.getNumPages() < page_nr:
            raise ApplicationError.InvalidArgument(
                "Bad page number: it should be < %s." %
                self._doc.getNumPages())
        import time
        self.logger.debug("Render image from pdf with opts width=%s, "\
            "height=%s, angle=%s, page_nr=%s." % (max_width, max_height, angle,
            page_nr))
        start = time.clock()
        splash = poppler.SplashOutputDev(poppler.splashModeRGB8, 3, False,
            (255, 255, 255), True, True)
        splash.startDoc(self._doc.getXRef())

        scale = self._get_optimal_scale(max_width, max_height, page_nr)
        self._doc.displayPage(splash, page_nr, 72*scale, 72*scale, -angle, True,
            True, False)

        bitmap = splash.getBitmap()
        new_width = bitmap.getWidth()
        new_height = bitmap.getHeight()
        import Image
        pil = Image.fromstring('RGB', (new_width, new_height),
            bitmap.getDataPtr())
        temp_file = cStringIO.StringIO()
        pil.save(temp_file, "JPEG", quality=90)
        temp_file.seek(0)
        content = temp_file.read()
        self.logger.debug("Total Process Time: %s", (time.clock() - start))
        #header = [('content-type', 'image/jpeg'), ('content-length',
        #str(len(content)))]
        return('image/jpeg', content)

# TODO: test
p = PdfProcessor('/examples/d05.pdf')
r = p.search(query='alors', from_=2, to_=100, max_results=0, sort=None)

if r:
    print "# results: %s"%(len(r['file_position']['results']))
else:
    print r
