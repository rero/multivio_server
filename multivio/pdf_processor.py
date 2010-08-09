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
        self._index = None

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

    def get_text(self, index=None):
        """Return the text contained inside the selected box.
            index -- dict: index in the document, including bounding box

        return:
            data -- string: output text
        """
        page_nr = index['page_number']

        td = poppler.TextOutputDev(None, True, False, False)
        self._doc.displayPage(td, page_nr, 72, 72, 0, True, True, False)
        text_page = td.takeText()        

        text = {}
        b = index['bounding_box']
        text['text'] = text_page.getText(b['x1'],b['y1'],b['x2'],b['y2'])
        return text

    def search(self, query, from_=None, to_=None, max_results=None, sort=None, context_size=None):
        """Search parts of the document that match the given query.

            from_ -- dict: start the search at from_
            to_ -- dict: end the search at to_
            max_results -- int: limit the number of the returned results
            sort -- string: sort the results given the sort criterion
            context_size: approximate number of characters of context around found words (left & right)
        return:
            a dictionary with the found results
        """  

        # number of results
        num_results = 0

        # number of pages in document
        num_pages = self._doc.getNumPages()        

        # conversion of search text to unicode
        query = unicode(query, 'utf-8')
        self.logger.debug("pdf_processor: searching term: [%s]"%query)

        ## findText options: perform find from top to bottom of page
        startAtTop = True
        stopAtBottom = True
        startAtLast = False
        stopAtLast = False
        caseSensitive = False
        backward = False

        # param check TODO report errors ?
        if (from_ is None): from_ = 1
        if (to_ is None): to_ = num_pages + 1   
        if (max_results in [0, None]):
            import sys 
            max_results = sys.maxint

        # calculate page range [1, num_pages+1]
        (from_, to_) = (max(from_, 1), min(to_ + 1, num_pages + 1))

        # results for the current file
        result = {
          'context': 'text',
          'file_position': {
            'url':self._file_name, # will be replaced by remote URL by processor app, if necessary
            'results':[ # results for that file go here
            ] 
          }
        }

        # current result
        cur_res = {}

        # note: to_ is not included in range
        done = False
        for np in xrange(from_, to_):
            # debug
            #self.logger.debug("pdf_processor: searching on page %d"%np)

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
                # build structure for the found word
                bbox = {'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2}

                # get context
                prw = self._get_context(np, bbox, text_page, context_size)

                cur_res = {
                  'preview': prw,
                  'index': {
                    'page': np, 
                    'bounding_box': bbox
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

    ## context/preview: get text left and right from found word
    # INFO: context_chars: approximate number of characters of context on each side of found word
    def _get_context(self, page_nr, bbox, text_page, context_chars = None):
    
        if (context_chars in [0, None]): 
            return ''

        # this allows us to get the words before and after
        # but we need to know the found word number first ...
        # words = text_page.makeWordList(True)
        # w = words.get(i)
        # word = w.getText()
        # (x1, y1, x2, y2) = w.getBBox()

        # get page dimensions
        page_size = self.get_size(index={'page_number': page_nr})

        # estimate of font size
        font_size = abs(bbox['y2']-bbox['y1'])

        #INFO: context_chars: approximate number of characters of context on each side of found word
        
        # define width according to font size
        context_width = 0.5*font_size*context_chars
        (x_before, x_after) = (max(0, bbox['x1']-context_width), min(page_size['width'], bbox['x2']+context_width))
        
        # get preview text
        prw = text_page.getText(x_before, bbox['y1'], x_after, bbox['y2'])
        # note: normally, prw is in utf-8 here. If not, do prw.encode('utf-8')

        return prw


    def get_indexing(self, index=None, from_=None, to_=None):
        """Returns index of a range of pages of the document.
        return:
            index structure of the page(s)
        """
        import time
        start = time.clock()

        result = {'pages':[]}

        # number of pages in document
        num_pages = self._doc.getNumPages()

        # if range specified, use it and ignore index['page_number']
        page_range = xrange(1,num_pages)
        if (None not in [from_, to_] and \
            '' not in [from_, to_]):

            # adapt to pages' range [1, num_pages]
            (from_, to_) = (max(from_, 1), min(to_, num_pages))

            for np in xrange(from_,to_+1):
                result['pages'].append(self._get_indexing(np))

        # else, try to use page_number in index
        else:
            page_nr = index['page_number']
            if (page_nr is not None and page_nr != '' and page_nr in page_range):
                result['pages'].append(self._get_indexing(page_nr))

        self.logger.debug("get_indexing: Total Process Time: %s", (time.clock() - start))

        return result

    def _get_indexing(self, page_nr=1):
        """Returns index of a page of the document.
        return:
            index structure of the page
        """

        # get words' list for a page
        td = poppler.TextOutputDev(None, True, False, False)
        self._doc.displayPage(td, page_nr, 72, 72, 0, True, True, False)
        text_page = td.takeText()
        words = text_page.makeWordList(True)

        # get page dimension
        page_size = self.get_size(index={'page_number': page_nr})

        # page structure
        page = {'page_number': page_nr, 'w': page_size['width'], 'h': page_size['height'], 'lines': []}
        #self.logger.debug("page dimensions: [%s,%s]"%(page_size['width'], page_size['height'] ))

        line = None            # current line structure
        line_start_x = -1      # horizontal position of the beginning of the line
        words_text = []        # list of words in current line
        import sys
        prev = {'y2':-1}
        x1 = y1 = x2 = y2 = 0
        for i in xrange(words.getLength()):

            # get current word
            w = words.get(i)
            coords = (x1, y1, x2, y2) = w.getBBox()
            # round values
            (x1, y1, x2, y2) = [round(x,0) for x in coords] 
            #self.logger.debug("new word [%s], coord:[%s,%s/%s,%s]"%(w.getText(), x1,y1,x2,y2))

            # detect new line based on line height
            if (y2 > prev['y2']):
                if (line is not None):
                    # separate each word by a space
                    line['text'] = ' '.join(words_text)
                    words_text = []
                    # compute line width
                    line['w'] = abs(prev['x2'] - line_start_x)
                    # store line in list
                    page['lines'].append(line)
                    #self.logger.debug("finished line: [%s]"%line['text'])

                # start a new line
                line = {'t':y1, 'l':x1, 'w':-1, 'h':abs(y2-y1), 'x':[], 'text':''}
                # keep line start, used to compute line width
                line_start_x = x1


            # store left and right coordinates of word
            line['x'].append({'l':x1,'r':x2})
            # store word in text list
            words_text.append(w.getText())

            # detect last word, and thus last line
            if (i == words.getLength()-1):
                # separate each word by a space
                line['text'] = ' '.join(words_text)
                words_text = []
                # compute line width
                line['w'] = abs(x2 - line_start_x)
                # store line in list
                page['lines'].append(line)
                #self.logger.debug("finished last line: [%s]"%line['text'])

            # update previous position
            prev = {'x1':x1,'y1':y1,'x2':x2,'y2':y2}
        
        return page

    def indexing(self, output_file):
        """Batch indexing of the document.
        return:
            True if everything is ok.
        """
        # format : {'word': {page_number, bbx}}
        index = {}
 
        import time
        start = time.clock()

        # number of pages in document
        num_pages = self._doc.getNumPages()

        self.logger.debug("indexing %s pages to file: %s"%(num_pages,output_file))

        # process each page
        for np in xrange(1,num_pages):

            #self.logger.debug("processing page number %s"%np)

            # get words' list for a page
            td = poppler.TextOutputDev(None, True, False, False)
            self._doc.displayPage(td, np, 72, 72, 0, True, True, False)
            text_page = td.takeText()
            words = text_page.makeWordList(True)
            
            # process each word
            for wi in xrange(words.getLength()):
                ww = words.get(wi)
                wt= ww.getText()
                coords = (x1,y1,x2,y2) = ww.getBBox()
                (x1,y1,x2,y2) = [round(x,0) for x in coords]

                # TODO: preprocess words, ie put everything to lower case, replace some characters...
                # remove punctuation
                wt = self._strip_punctuation(wt.lower())

                if (len(wt.strip())==0): 
                    continue

                # check for existing entry of word in index
                if index.has_key(wt):
                    index[wt].append({'page_number':np, 'bbx':{'x1':x1,'y1':y1,'x2':x2,'y2':y2}})
                else:
                    index[wt] = [{'page_number':np, 'bbx':{'x1':x1,'y1':y1,'x2':x2,'y2':y2}}]

        # store index in processor instance
        self._index = index 

        self.logger.debug("Total Indexing Time: %s", (time.clock() - start))

        import sys
        if sys.version_info < (2, 6):
            import simplejson as json
        else:
            import json

        self.logger.debug("writing to file: %s"%output_file)

        start = time.clock()

        # output to file
        f = open(output_file,'w')
        data = json.dumps(index, sort_keys=True, encoding='utf-8', indent=2)
        f.write(data)
        f.close()

        self.logger.debug("Total Save Index to File Time: %s", (time.clock() - start))

        return True

    def _strip_punctuation(self, text):
        import string
        not_letters_or_digits = string.punctuation  # '!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'
        if isinstance(text, unicode):
            translate_table = dict((ord(c), u'')
                               for c in unicode(not_letters_or_digits))
            return text.translate(translate_table)
        else:
            assert isinstance(text, str)
            translate_table = string.maketrans("","")
            return text.translate(translate_table, not_letters_or_digits)


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
p = PdfProcessor('/examples/d04.pdf')
#r = p.search(query='été', from_=1, to_=50, max_results=0, sort=None, context_size=10)
#
#if r:
#    print "# results: %s"%(len(r['file_position']['results']))

p.indexing('/tmp/index_output')
#page = p.get_indexing(page_nr=1)
