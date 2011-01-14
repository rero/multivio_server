#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test for the Multivio logger.
"""
#==============================================================================
#  This file is part of the Multivio software.
#  Project  : Multivio - https://www.multivio.org/
#  Copyright: (c) 2009-2011 RERO (http://www.rero.ch/)
#  License  : See file COPYING
#==============================================================================

# standard modules
import sys
import os
import unittest

# local modules
from mvo_config import MVOConfig
if os.path.isfile(MVOConfig.Logger.file_name):
    os.remove(MVOConfig.Logger.file_name)

# add the current path to the python path, so we can execute this test
# from any place
sys.path.append (os.getcwd ())
import multivio.logger
import logging


class LoggerOK (unittest.TestCase):
    """
    Test Logger Class.
    """
    #def setUp(self):
    #    if os.path.isfile(MVOConfig.Logger.file_name):
    #        os.remove(MVOConfig.Logger.file_name)

    def testLogger(self):
        """Check logger instance."""
        logger = logging.getLogger(MVOConfig.Logger.name + "." + "Test")
        self.assert_ (logger, "Can not create simple Logger Object")
    
    #def testLoggerBadFile(self):
    #    """Check logger instance with bad file."""
    #    bad_file_name = '/cannotexists/this/file.log'
    #    MVOConfig.Logger.file_name = bad_file_name
    #    self.assertRaises(multivio.logger.LoggerError.InvalidFileName,
    #        reload, multivio.logger)
    
    def testAddLog(self):
        """Add a simple log."""
        before_n_lines = len(file(MVOConfig.Logger.file_name).readlines())
        logger = logging.getLogger(MVOConfig.Logger.name + "." + "Test")
        logger.info("Info1")
        logger.info("Info2")
        logger.debug("Debug1")
        logger.debug("Debug2")
        after_n_lines = len(file(MVOConfig.Logger.file_name).readlines())
        #lines = file(MVOConfig.Logger.file_name).readlines()
        n_lines = after_n_lines - before_n_lines
        self.assertEqual(4, n_lines, "The log has not be written in"\
                        "the file. (%s != %s)" % (4, n_lines))
    
    #def tearDown(self):
    #    if os.path.isfile(MVOConfig.Logger.file_name):
    #        os.remove(MVOConfig.Logger.file_name)
        

if __name__ == '__main__':
    # the main program if we execute directly this module

    # do all the tests
    unittest.main()
