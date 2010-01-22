#!/usr/bin/env python

# -*- coding: utf-8 -*-

__author__ = 'Johnny Mariethoz <Johnny.Mariethoz@rero.ch>'
__version__ = '0.0.0'
__copyright__ = 'Copyright (c) 2009 Rero, Johnny Mariethoz'
__license__ = 'Internal Use Only'


#---------------------------- Modules -----------------------------------------

# import of standard modules
import sys
import os
from optparse import OptionParser
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json

# third party modules


# local modules

class CoreDocumentModel(dict):
    def __init__(self, counter=1):
        dict.__init__(self)
        self._counter = counter
        self._node_name = 'n%05d'
    
    def addNode(self, parent_id=None, label=None,
                metadata=None, url=None, sequenceNumber=None,
                localSequenceNumber=None):
        current_id = self._node_name % self._counter

        to_add = {
               'guid': current_id, 
               }
        if metadata is not None:
            to_add['metadata'] = metadata
        if label is not None:
            to_add['label'] = label
        if url is not None:
            to_add['urlDefault'] = url
        if sequenceNumber is not None:
            to_add['sequenceNumber'] = sequenceNumber
        if localSequenceNumber is not None:
            to_add['localSequenceNumber'] = localSequenceNumber
        if isinstance(parent_id, str):
            parent_id = [parent_id]
        if parent_id is not None and len(parent_id) > 0:
            for pi in parent_id:
                parent = self[pi]
                if not parent.has_key('children'):
                    parent['children'] = []
            
                if not to_add.has_key('parentId'):
                    to_add['parentId'] = []
                to_add['parentId'].append(pi)
                parent['children'].append(current_id)
        else:
            to_add['parentId'] = []
            self._root = current_id
        self[current_id] = to_add
        self._counter = self._counter + 1
        return current_id
    
    def printStructure(self, branch_id=None, padding=' '):
        if branch_id is None:
            branch_id = self._root
        print padding[:-1] + '+-' + branch_id
        padding = padding + ' '
        if self[branch_id].has_key('children'):
            children = self[branch_id]['children'] 
            count = 0
            for child in children:
                count += 1
                print padding + '|'
                if count == len(children):
                    self.printStructure(child, padding + ' ')
                else:
                    self.printStructure(child, padding + '|')

#---------------------------- Main Part ---------------------------------------

if __name__ == '__main__':

    usage = 'usage: %prog [options]'

    parser = OptionParser(usage)

    parser.set_description ('Change It')



    parser.add_option ('-v', '--verbose', dest='verbose',
                       help='Verbose mode',
                       action='store_true', default=False)


    (options,args) = parser.parse_args ()

    if len(args) != 0:
        parser.error('Error: incorrect number of arguments, try --help')


    t = CoreDocumentModel()
    root_id = t.addNode()
    a = t.addNode(root_id)
    b = t.addNode(a)
    c = t.addNode(root_id)
    t.printStructure()
    print json.dumps(t, sort_keys=True, indent=4)
