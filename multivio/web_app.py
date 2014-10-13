#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base class for all wsgi web applications."""

#==============================================================================
#  This file is part of the Multivio software.
#  Project  : Multivio - https://www.multivio.org/
#  Copyright: (c) 2009-2011 RERO (http://www.rero.ch/)
#  License  : See file COPYING
#==============================================================================

__copyright__ = "Copyright (c) 2009-2011 RERO"
__license__ = "GPL V.2"

#---------------------------- Modules -----------------------------------------

# import of standard modules
import os
import cgi
import re
import hashlib
import urllib
import time
import logging

from mvo_config import MVOConfig
import mvo_config


#------------- Exceptions -------------------------
class WebException(Exception):
    """Base class for errors in web application."""
    def __init__(self, value=None):
        self.value = value
        self.http_code = None
    def __str__(self):
        return repr(self.value)

class ApplicationError:
    """Prefix to import all exceptions."""

    class UnableToRetrieveRemoteDocument(WebException):
        """Problem with the remote server.
            HTTP: 502
        """
        def __init__(self, value=None):
            WebException.__init__(self, value)
            self.http_code = "502 Bad Gateway"

    class UnsupportedFormat(WebException):
        """Unsupported file format.
            HTTP: 415
        """
        def __init__(self, value=None):
            WebException.__init__(self, value)
            self.http_code = "502 Bad Gateway"

    class PermissionDenied(WebException):
        """
            HTTP: 403
        """
        def __init__(self, value=None):
            WebException.__init__(self, value)
            self.http_code = "502 Bad Gateway"

    class InvalidArgument(WebException):
        """
            HTTP: 400
        """
        def __init__(self, value=None):
            WebException.__init__(self, value)
            self.http_code = "502 Bad Gateway"
    
    class HttpMethodNotAllowed(WebException):
        """
            HTTP: 405 Method Not Allowed
        """
        def __init__(self, value=None):
            WebException.__init__(self, value)
            self.http_code = "405 Method Not Allowed"

#-------------------- Utils ------------------------ 
class MyFancyURLopener(urllib.FancyURLopener):
    """Class to intercept 404 HTTP error."""


    def __init__(self, user_agent=None):
        if user_agent is not None:
            MyFancyURLopener.version = user_agent
        urllib.FancyURLopener.__init__(self)
        self.cookies = []

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        """To catch HTTP Errors."""
        if errcode == 404:
            raise ApplicationError.UnableToRetrieveRemoteDocument(errmsg)

    def open_http(self, url, data=None):
        """Handle an HTTP open request.  We pass this to FancyURLopener
to do
           the real work.  Afterwards, we scan the info() for
cookies."""
        result = urllib.FancyURLopener.open_http(self, url, data)
        self.eatCookies(result.info())
        return result

    def http_error_302(self, url, fp, errcode, errmsg, headers, data=None):
        """Handle an HTTP redirect.  First we get the cookies from the headers
           off of the initial URL.  Then hand it off to the super-class, which
           will call back into our open_http method, where we can pick up
           more cookies."""
        self.eatCookies(headers)
        result = urllib.FancyURLopener.http_error_302(self, url, fp, errcode,
                errmsg, headers, data=None)
        return result

    def eatCookies(self, headers):
        """Scan a set of response headers for cookies.  We add each cookie to
           our list."""
        cookies = headers.getallmatchingheaders('set-cookie')
        for c in cookies:
            # "set-cookie: " is 11 characters
            self.addCookie(":".join(c.split(':')[1:])) 

    def addCookie(self, cookie):
        """Add a cookie to our cache of them and call addheaders of our
           parent.
        """
        self.cookies.append(cookie)
        self.addheader('Cookie', cookie)


class InputProcessed(object):
    """To read the body of a post HTTP message."""

    def read(self, *args):
        """To provide stream."""
        raise EOFError('The wsgi.input stream has already been consumed')
    readline = readlines = __iter__ = read

#-------------------- Main Classes ------------------------ 
class WebApplication(object):
    """Base class for all wsgi web applications."""

    def __init__(self, temp_dir=MVOConfig.General.temp_dir):
        self.usage = """<br><h1>Welcome to the multivio server.</h1>
        This is an abstract base class. Do not use it!
"""
        self._tmp_dir = temp_dir
        self._timeout = MVOConfig.Url.timeout
        import socket
        socket.setdefaulttimeout(self._timeout)
        self.request = (None, None)
        self._urlopener = MyFancyURLopener(MVOConfig.Url.user_agent)
        #self._urlopener.version = MVOConfig.Url.user_agent
        self.logger = logging.getLogger(MVOConfig.Logger.name + "."
                        + self.__class__.__name__) 
        self._supported_mime = [
            r".*?/pdf.*?",
            r".*?/xml.*?",
            r"image/.*?"]
        self.cookies = None

    def get(self, environ, start_response):
        """Methods to call when a GET HTTP request should be served."""
        raise ApplicationError.HttpMethodNotAllowed("GET method is not allowed.")

    def post(self, environ, start_response):
        """Methods to call when a POST HTTP request should be served."""
        post_form = self.get_post_form(environ)
        raise ApplicationError.HttpMethodNotAllowed("POST method is not allowed.")
    
    def get_params(self, environ):
        """Parse cgi parameters."""
        path = environ['PATH_INFO']
        opts = cgi.parse_qs(environ['QUERY_STRING'])
        return (path, opts)

    def __call__(self, environ, start_response):
        """Main wsgi method."""
        self.request = (environ, start_response)
        self.cookies = environ.get('HTTP_COOKIE', None)

        if re.match('.*?help.*?', environ['PATH_INFO']):
            start_response('200 OK', [('content-type', 'text/html')])
            return [self.usage]
            
        if environ['REQUEST_METHOD'].upper() == 'GET':
            return self.get( environ, start_response)

        if environ['REQUEST_METHOD'].upper() == 'POST':
            return self.post( environ, start_response)

        start_response('405 Method Not Allowed', [('content-type',
                        'text/html')])
        self.request = (None, None)
        return ["%s is not allowed." % environ['REQUEST_METHOD'].upper()]

    def check_mime(self, mime):
        """Check if the mime type is supported."""
        if not [ re.match(regex, mime) for regex in self._supported_mime
                if re.match(regex, mime)]:
            raise ApplicationError.UnsupportedFormat(
                "Mime type: %s is not supported" % mime)

    def get_remote_file(self, url, force=False, request=None):
        """Get a remote file if needed and download it in a cache directory."""
        #file in RERO DOC nfs volume
        try:
            (mime, local_file) = mvo_config.get_internal_file(url, force, 
                    self.request)

            if not isinstance(local_file, basestring):
                self.check_mime(mime)
                self.logger.info("Memory file!")
                return (local_file, mime)

            if local_file is not None and os.path.isfile(local_file):
                self.check_mime(mime)
                self.logger.info("Found local file: %s" % local_file)
                return (local_file, mime)
        except (NameError, AttributeError):
            pass
        
        url_md5 = hashlib.sha224(url).hexdigest()
        self.logger.debug('Temp dir: %s' % self._tmp_dir)
        local_file = os.path.join(self._tmp_dir, url_md5)

        #remote file
        mime_file = local_file + ".mime"
        to_download = False
        try:
            #file exists: ATOMIC?
            os.open(local_file, os.O_CREAT|os.O_EXCL|os.O_RDWR)
            to_download = True
        except Exception:
            pass

        if to_download:
            self.logger.debug("Try to retrieve %s file" % url)
            start = time.time()
            if self.cookies is not None:
                self._urlopener.addheaders.append(("Cookie", self.cookies))
            try:
                (filename, headers) = self._urlopener.retrieve(url,
                    local_file+".tmp")
                end = time.time()
                self.logger.info("Total Downloading Time: %s,"\
                    " Connection speed: %s KB/s " % (end-start,
                    os.path.getsize(filename)/((end-start)*1024.)))
                self.logger.info("%s downloaded into %s" % (url, local_file))
            except Exception, e:
                os.remove(local_file)
                raise ApplicationError.UnableToRetrieveRemoteDocument(str(e))
                
            #save mime type in cache
            mime = headers['Content-Type']
            if re.match('.*?/x-download', mime):
                mime = 'application/pdf'
            output_mime_file = file(mime_file, "w")
            output_mime_file.write(mime)
            output_mime_file.close()

            #file in cache
            os.rename(filename, local_file)
        else:
            #downloading by an other process?
            start_time_wait = time.time() 
            time_out_counter = 0
            while os.path.getsize(local_file) == 0L \
                and time_out_counter < self._timeout:
                self.logger.info("Wait for file: %s" % local_file )
                time.sleep(.5)
                time_out_counter = time.time() - start_time_wait
            if time_out_counter >= self._timeout:
                self.logger.warn("Uploading process timeout")
                raise ApplicationError.UnableToRetrieveRemoteDocument(
                    "Uploading process timeout: %s" % url)
        
        #load mime type
        output_mime_file = file(mime_file, "r")
        mime = output_mime_file.read()
        output_mime_file.close()

        self.check_mime(mime)

        self.logger.debug("Url: %s Mime: %s LocalFile: %s" % (url, mime,
                local_file))

        return (local_file, mime)
        
#---------------------- to update when the remote file is modified ---------
        #is file exists?
        #if os.path.isfile(local_file):
        #    stats = os.stat(local_file)
        #    diff_last_access = datetime.timedelta(seconds=now -
        #            stats[7])
        #    diff_last_modif = datetime.timedelta(seconds=now -
        #            stats[8])
        #    self.logger.debug("Last access: %s, last_modif: %s" %
        #        (diff_last_access, diff_last_modif))

        #    #check for update every xx seconds
        #    if diff_last_modif > datetime.timedelta(seconds=20):
        #        #get remote file size
        #        url_f = self._urlopener.open(url)
        #        http_header = url_f.info()
        #        remote_file_size = -1
        #        self.logger.debug("Header: %s" % http_header.keys())
        #        if http_header.has_key('content-length'):
        #            remote_file_size = int(http_header['content-length'])
        #        url_f.close()

        #        self.logger.debug("Remote file_size: %s local file size: %s" %
        #            (remote_file_size, stats[6]))
        #        #check if size has changed
        #        if remote_file_size != int(stats[6]) and \
        #            diff_last_access > datetime.timedelta(seconds=10):
        #                #check if someone did an access xx seconds ago
        #                #!!Not atomic
        #                os.rename(local_file, local_file+".to_remove")
        #                os.remove(local_file+".to_remove")
        #                self.logger.debug("Update file.")
        #os.utime(local_file, (now, os.stat(local_file)[8]))


    def get_post_form(self, environ):
        """For POST HTTP request."""
        wsgi_input = environ['wsgi.input']
        post_form = environ.get('wsgi.post_form')
        if (post_form is not None
            and post_form[0] is wsgi_input):
            return post_form[2]
        fs = cgi.FieldStorage(fp=wsgi_input,
                              environ=environ,
                              keep_blank_values=1)
        new_input = InputProcessed()
        post_form = (new_input, wsgi_input, fs)
        environ['wsgi.post_form'] = post_form
        environ['wsgi.input'] = new_input
        return fs
