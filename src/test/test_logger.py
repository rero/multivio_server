#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit test for the verif scores module.

This file is part of the pyMeasure scripts module.
"""

# some general value for this module
__author__ = "Johnny Mariethoz <Johnny.Mariethoz@idiap.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"

# standard modules
import sys
import os
import unittest
import ConfigParser
import json

# local modules
import multivio

# add the current path to the python path, so we can execute this test
# from any place
sys.path.append (os.getcwd ())

file_name = '/tmp/multivio.log'

class LoggerOK (unittest.TestCase):
    """
    Test Logger Class.
    """

    def testLogger(self):
        """Check logger instance."""
        logger = multivio.Logger(file_name)
        self.assert_ (logger, "Can not create simple Logger Object")
    
    def testLoggerBadFile(self):
        """Check logger instance with bad file."""
        bad_file_name = '/cannotexists/this/file.log'
        self.assertRaises(multivio.logger.LoggerError.InvalidLogFile,
            multivio.Logger, file_name=bad_file_name)
    
    def testAddLog(self):
        """Add a simple log."""
        header = 'Header'
        content = {'msg': 'test'}
        body_in_json = json.dumps(content)
        logger = multivio.Logger(file_name)
        current_size = os.path.getsize(file_name)
        new_supposed_size = current_size + len(header) + len(body_in_json) + 8
        logger.addLog(header, body_in_json)
        new_size = os.path.getsize(file_name)
        self.assertEqual(new_supposed_size, new_size, "The log has not be written in"\
                        "the file. (%s != %s)" % (new_size, new_supposed_size))
    
    def tearDown(self):
        if os.path.isfile(file_name):
            os.unlink(file_name)
        

if __name__ == '__main__':
    # the main program if we execute directly this module

    # do all the tests
    unittest.main()
