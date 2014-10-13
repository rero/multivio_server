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
import os.path

# local modules
from processor import DocumentProcessor
import poppler
from web_app import ApplicationError
from mvo_config import MVOConfig
try:
    import Image
except:
    from PIL import Image

#----------------------------------- Exceptions --------------------------------

#----------------------------------- Classes -----------------------------------

#_______________________________________________________________________________
class PdfProcessor(DocumentProcessor):
    """Class to process pdf document"""
#_______________________________________________________________________________
    def __init__(self, file_name):
        DocumentProcessor.__init__(self, file_name)
        poppler.cvar.globalParams.setEnableFreeType("yes")
        poppler.cvar.globalParams.setErrQuiet(True)
        poppler.cvar.globalParams.setAntialias("yes")
        poppler.cvar.globalParams.setVectorAntialias("yes")
        self._doc = poppler.PDFDoc(self._file_name)
        self._index = None

        # store url md5
        # NOTE: assuming the name of the file given is the md5 of the url
        self._url_md5 = os.path.split(self._file_name)[1]
        #self.logger.debug("PDFProcessor, got url_md5=[%s]"%self._url_md5)

        # keyword for boolean search
        self._AND = ' and'


    def _check(self):
        """Check if the document is valid."""
        return True

    def render(self, max_output_size=None, angle=0, index=None,
        output_format=None, restricted=False):
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
            angle=angle, output_format=output_format, restricted=restricted)
    
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

    def get_text(self, index=None, angle=0):
        """Return the text contained inside the selected box.
            index -- dict: index in the document, including 'bounding_box'
            angle -- int: rotation angle, 0, +-90, +- 180, +-270
        return:
            data -- string: output text
        """

        page_nr = index['page_number']

        # get page text
        td = poppler.TextOutputDev(None, True, False, False)
        self._doc.displayPage(td, page_nr, 72, 72, -angle, True, True, False)
        text_page = td.takeText()
    
        # get text inside given bounding box
        text = {}
        b = index['bounding_box']
        text['text'] = text_page.getText(b['x1'],b['y1'],b['x2'],b['y2'])
        return text

    def search(self, query, from_=None, to_=None, max_results=None, sort=None, context_size=None, angle=0):
        """Search parts of the document that match the given query.

            query -- string: text to find in the document
            from_ -- integer: start the search at page from_
            to_ -- integer : end the search at page to_
            max_results -- integer: limit the number of the returned results
            sort -- string: sort the results given the sort criterion
            context_size -- integer: approximate number of characters of context around found words (left & right)
            angle -- integer: angle of display in degrees
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

        # create sub queries separated by boolean keywords, if necessary
        boolean_search = query.find(self._AND) != -1
        queries = [x.strip() for x in query.lower().split(self._AND) if len(x) > 0]

        ## findText options: perform find from top to bottom of page
        startAtTop = True
        stopAtBottom = True
        startAtLast = False
        stopAtLast = False
        caseSensitive = False
        backward = False

        # param check. TODO report errors ?
        if (from_ is None): from_ = 1
        if (to_ in [0, -1, None]): to_ = num_pages + 1
        if (max_results in [0, None]):
            # TODO: config for upper limit
            #import sys
            max_results = 50 #sys.maxint

        # calculate page range [1, num_pages+1]
        (from_, to_) = (max(from_, 1), min(to_ + 1, num_pages + 1))

        # results for the current file
        result = {
          'max_reached': 0,
          'context': 'text',
          'file_position': {
            'url':self._file_name, # will be replaced by remote URL by processor_app, if necessary
            'results':[ # results for that file go here
            ]
          }
        }
        
        # current result
        cur_res = {}

        # note: to_ is not included in range
        all_done = False
        for np in xrange(from_, to_):

            self.logger.debug("pdf_processor: searching on page %d"%np)

            # results for the current page, all subqueries
            page_results = []

            if all_done is True:
                break

            td = poppler.TextOutputDev(None, True, False, False)
            # NOTE: always do search and context retrieval without rotation,
            # and compute final coordinates at the end
            self._doc.displayPage(td, np, 72, 72, 0, True, True, False)

            # get page dimensions
            page_size = self.get_size(index={'page_number': np})

            text_page = td.takeText()
            
            # search for all sub-queries
            lq = len(queries)
            for i in xrange(0, lq):
            
                subquery = queries[i]
            
                self.logger.debug("pdf_processor: searching subquery: %s on page %s..."%(subquery, np))
            
                ## findText options: for each word, start at top of page
                startAtTop = True
                stopAtBottom = True
                startAtLast = False
            
                # store coordinates
                coords = (found, x1, y1, x2, y2) = text_page.findText(subquery, startAtTop, stopAtBottom, startAtLast, stopAtLast, caseSensitive, backward)
                coords = coords[1:] # don't keep found boolean
    
                # boolean: if a subquery is not found, no need to look for the other subqueries 
                # on this page (NOTE: only for AND, for now...)
                # discard all the previous results found on this page (ie store them only after we 
                # found at least 1 result for the last subquery on the page).
                if (not found):
                    self.logger.debug("pdf_processor: word %s not found on page %s, skipping"%(subquery, np))               
                    break
    
    
                ## findText options: find from last find to bottom of page
                startAtTop = False
                stopAtBottom = True
                startAtLast = True
      
                # keep searching on this page
                while found is True:
                
                    self.logger.debug("pdf_processor: found word %s on page %s, building structure"%(subquery, np))
                
                    # build structure for the found word (round coordinates to ints)
                    (x1, y1, x2, y2) = [round(x,0) for x in coords]
                    bbox = {'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2}
    
                    # get context
                    prw = self._get_context(np, bbox, text_page, context_size)
    
                    # store coordinates, taking angle into account
                    cur_res = {
                      'preview': prw,
                      'index': {
                        'page': np,
                        'bounding_box': self._get_coords(bbox, angle, page_size)
                      }
                    }
                    
                    # append result to list
                    # boolean: current page results, may be discarded if a subquery is not found
                    page_results.append(cur_res)
                                    
                    num_results = num_results + 1
                    if (num_results >= max_results):
                        all_done = True
                        result['max_reached'] = max_results
                        break
                    # find additional words on page
                    coords = (found, x1, y1, x2, y2) = text_page.findText(subquery, startAtTop, stopAtBottom, startAtLast, stopAtLast, caseSensitive, backward)
                    coords = coords[1:] # don't keep found boolean
                    

                # last subquery was found on the page, we can add the results to the global results list now
                if (i == (lq - 1)):
                    self.logger.debug("pdf_processor: word %s found on page %s, adding to global results"%(subquery, np))
                    result['file_position']['results'].extend(page_results)
                

        return result

    def _get_coords(self, bbox, angle, page_size):
       """Adapt coordinates according to given rotation angle and page size.
          Only orthogonal rotations are supported:
                                0, +-90, +-180, +-270 degrees.

           bbox -- dict: bounding box coordinates
           angle -- int: rotation angle in degrees
           page_size -- dict: page size (with 'width' and 'height')
       return:
           data -- dict: a dictionary with the adapted bounding box
       """

       # get coordinates
       (x1, y1, x2, y2) = (bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2'],)

       # rotation to the right
       if (angle in [-90, 270]):
           bbox['x1'] = max(0, page_size['height'] - y2)
           bbox['y1'] = x1
           bbox['x2'] = max(0, page_size['height'] - y1)
           bbox['y2'] = x2

       # rotation to the left
       elif (angle in [90, -270]):
           bbox['x1'] = y1
           bbox['y1'] = max(0, page_size['width'] - x2)
           bbox['x2'] = y2
           bbox['y2'] = max(0, page_size['width'] - x1)

       # rotation upside-down
       elif (angle in [-180, 180]):
           bbox['x1'] = max(0, page_size['width'] - x2)
           bbox['y1'] = max(0, page_size['height'] - y2)
           bbox['x2'] = max(0, page_size['width'] - x1)
           bbox['y2'] = max(0, page_size['height'] - y1)
       
       self.logger.debug('get_coords: angle: %d, (%d,%d), (%d,%d), w:%d, h:%d'\
               % (angle, x1,y1,x2,y2, page_size['width'], page_size['height']))

       return bbox

    def _get_context(self, page_nr, bbox, text_page, num_chars = None):
        """Context/preview: get text left and right from found word.
           'num_chars' are taken on the left and right sides of the word
           specified by the bounding box 'bbox'. This number is approximate
           and can vary, depending on font size and page dimensions.

           NOTE: the given 'text_page' must have a rotation angle of 0!

            page_nr -- int: page number
            bbox -- dict: bounding box coordinates of word
            text_page -- poppler text page instance
            num_chars -- int: number of context chars on each side of the word
        return:
            data -- string: output text
        """

        if (num_chars in [0, None]):
            return ''

        # this allows us to get the words before and after
        # but we need to know the found word number first ...
        # words = text_page.makeWordList(True)
        # w = words.get(i)
        # word = w.getText()
        # (x1, y1, x2, y2) = w.getBBox()

        # get page dimensions
        page_size = self.get_size(index={'page_number': page_nr})

        # get coordinates
        (x1, y1, x2, y2) = (bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2'],)

        #self.logger.debug("get_context: %s, %s, %s, %s" % (x1, y1, x2, y2))

        # estimate font size (assuming content is not rotated or upside down)
        font_size = abs(y2-y1)
    
        # define width/height according to font size
        context_size = 0.5*font_size*num_chars
        (x1c, y1c, x2c, y2c) = (max(0, x1-context_size), y1,\
                                min(page_size['width'], x2+context_size), y2)
        
        # get preview text
        prw = text_page.getText(x1c, y1c, x2c, y2c)
        # note: normally, prw is in utf-8 here. If not, do prw.encode('utf-8')

        return prw


    def get_indexing(self, index=None, from_=None, to_=None):
        """Returns index of a range of pages of the document.
           If a range of pages is specified with 'from_' and 'to_',
           'index' is ignored. Else, page number in index is used.

            index -- dict: index indicating a page number
            from_ -- int: page number start
            to_ -- int: page number end
        return:
            data -- dict: index structure of the page(s)
        """

        import time
        start = time.clock()

        result = {'pages':{}}

        # number of pages in document
        num_pages = self._doc.getNumPages()

        # if range specified, use it and ignore index['page_number']
        page_range = xrange(1,num_pages + 1)
        if (0    not in [from_, to_] and \
            None not in [from_, to_] and \
            ''   not in [from_, to_]):

            # adapt to pages' range [1, num_pages]
            (from_, to_) = (max(from_, 1), min(to_, num_pages))

            for np in xrange(from_,to_+1):
                result['pages'][np] = self._get_indexing(np)

        # else, try to use page_number in index
        else:
            page_nr = index['page_number']
            if (page_nr is not None and page_nr != ''\
                      and page_nr in page_range):
                result['pages'][page_nr] = self._get_indexing(page_nr)

        self.logger.debug("get_indexing: Total Process Time: %s",\
                                            (time.clock() - start))

        return result

    def _get_indexing(self, page_nr=1):
        """Returns index of a page of the document.

            page_nr -- int: number of the page

        return:
            data -- dict: index structure of the page
        """

        # get words' list for a page
        # TextOutputDev(char *fileName, GBool physLayoutA, 
        #               GBool rawOrderA, GBool append)
        # NOTE: use physical layout and raw order of words in the page
        td = poppler.TextOutputDev(None, True, True, False)
        self._doc.displayPage(td, page_nr, 72, 72, 0, True, True, False)
        text_page = td.takeText()
        # use physical layout to make word list
        # TextWordList *makeWordList(GBool physLayout)
        words = text_page.makeWordList(True)

        # get page dimension
        page_size = self.get_size(index={'page_number': page_nr})

        # page structure
        page = {'page_number': page_nr, \
                'w': page_size['width'],\
                'h': page_size['height'],\
                'lines': []}
        #self.logger.debug("page dimensions: [%s,%s]"\
        # %(page_size['width'], page_size['height'] ))

        line = None # current line structure
        line_start_x = -1 # horizontal position of beginning of the line
        words_text = [] # list of words in current line
        import sys
        prev = {'x1':-1,'y1':-1,'x2':-1,'y2':-1}
        x1 = y1 = x2 = y2 = 0
        for i in xrange(words.getLength()):

            # get current word
            w = words.get(i)
            coords = (x1, y1, x2, y2) = w.getBBox()
            # round values
            (x1, y1, x2, y2) = [round(x,0) for x in coords]
            #self.logger.debug("new word [%s], coord:[%s,%s/%s,%s]"\
            # %(w.getText(), x1,y1,x2,y2))

            # compute height difference with previous line
            hdiff = prev['y2'] - y2
            # compute current line height
            line_height = abs(y2-y1)

            # detect new line based on height, keep a few pixels margin,
            # half of line height but at least 2 pixels
            margin = max(0.5 * line_height, 2)
            if (abs(hdiff) > margin):
                if (line is not None):
                    # separate each word by a space
                    line['text'] = ' '.join(words_text)
                    words_text = []
                    # store line right coordinate
                    line['r'] = prev['x2']
                    # may need to adapt line top and height (for example 
                    # if the first element was a superscript)
                    line['h'] = abs(prev['y2'] - line['t'])
                    # store line in list
                    page['lines'].append(line)
                    #self.logger.debug("finished line: [%s]"%line['text'])

                # start a new line
                line = {'t':y1, 'l':x1, 'r':-1,\
                        'h':line_height, 'x':[], 'text':''}

                # keep line start, used to compute line width
                line_start_x = x1

            # NOTE: check if word of current line is coherent with previous one
            # if previous word is further down in the page than the current, 
            # it's probably wrong, remove it and redo line from scratch
            # this can typically happen on the first line of a page, where
            # 'rogue' elements such as page number in footer appear at
            # the beginning of the word list.
            # difference should be zero in normal cases
            # if difference more than 10% of page height,
            # it's either a rogue word or first word on a new line
            if (hdiff > 0.1 * page['h']):
                #self.logger.debug('--> redo line')
                words_text = []
                line['x'] = [] 
                line_start_x = x1
                line['t'] = y1
                line['l'] = x1
                line['h'] = line_height
            
            # store left and right coordinates of word
            line['x'].append({'l':x1,'r':x2})
            # store word in text list
            words_text.append(w.getText())

            # detect last word, and thus last line
            if (i == words.getLength()-1):
                # separate each word by a space
                line['text'] = ' '.join(words_text)
                words_text = []
                # store line right coordinate
                line['r'] = x2
                # may need to adapt line top and height (for example 
                # if the first element was a superscript)
                line['h'] = abs(y2 - line['t'])
                # store line in list
                page['lines'].append(line)
                #self.logger.debug("finished last line: [%s]"%line['text'])

            # update previous position
            prev = {'x1':x1,'y1':y1,'x2':x2,'y2':y2}
        
        return page

    def indexing(self, output_file):
        """Batch indexing of the document.

           output_file -- string: path of file to save indexing to
 
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

        # process each page
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
                # round values
                (x1,y1,x2,y2) = [round(x,0) for x in coords]

                # TODO?: preprocess words, ie put everything to lower case,
                # replace some characters, remove punctuation
                wt = self._strip_punctuation(wt.lower())

                if (len(wt.strip())==0):
                    continue

                # check for existing entry of word in index
                if index.has_key(wt):
                    index[wt].append({'page_number':np, \
                                      'bbx':{'x1':x1,'y1':y1,'x2':x2,'y2':y2}})
                else:
                    index[wt] = [{'page_number':np, \
                                  'bbx':{'x1':x1,'y1':y1,'x2':x2,'y2':y2}}]

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

        self.logger.debug("Total Save Index to File Time: %s",\
                                            (time.clock() - start))

        return True

    def _strip_punctuation(self, text):
        """Strip punctuation characters from given text.

            text -- string: text to remove punctuation from

        return:
            text -- string: text without punctuation
        """

        import string
        not_letters_or_digits = string.punctuation
        # '!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'

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
        if(int(self._doc.getPageRotate(page_nr)) % 180 == 90 ):
            page_width, page_height = page_height, page_width
            
        self.logger.debug("Width: %s, Height: %s, page_nr: %s, rotation: %s" %(page_width,
            page_height, page_nr, self._doc.getPageRotate(page_nr)))
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
        angle=0, output_format='JPEG', restricted=False):
        """Render a pdf page as image."""
        if restricted and (page_nr > 1):
            raise ApplicationError.PermissionDenied(
                "Your are not allowed to see this document.")

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
        if restricted and ((MVOConfig.Security.pdf_max_width < new_width)\
                or (MVOConfig.Security.pdf_max_height < new_height)):
            raise ApplicationError.PermissionDenied(
                "Your are not allowed to see this document.")

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
