Multivio Server
===============
Johnny Mariethoz <Johnny.Mariethoz@rero.ch>
V. 0.0, 2009/11/26

== Introduction ==
Python based multivio server.

== Installation ==

.An Used packages
[width="80%",frame="topbot",options="header"]
|========================================================================================================================
|Packages   |Documentation                                    |Licence    |2.5 Installation          |2.6 Installation
|wsgiref    |http://docs.python.org/library/wsgiref.html      |PSF-2      |easy_install wsgiref      |default
|json       |http://docs.python.org/library/json.html         |PSF-2      |easy_install simplejson   |default
|PIL        |http://www.pythonware.com/products/pil           |MIT like   |setup.py                  |easy_install
|pdfminer   |http://www.unixuser.org/~euske/python/pdfminer   |MIT/X      |setup.py                  |setup.py
|gfx        |http://www.swftools.org/gfx_tutorial.html        |GPL2       |./configure               |./configure
|========================================================================================================================

The PIL library need also libjpeg as describe in the PIL documentation.

The gfx package should first be compiled using ./configure. In macosx, I got
an error and I should to run ranlib on lib/*.a. The lib/python/*.so
files should be copied by hand in a python library directory.

== With apache ==
You have to copy the dispatcher.py in an apache web directory: i.e.
$HOME/Sites.

Modify the apache config by adding a line containing:
=====================
---------------------
WSGIScriptAlias /mvo_server /ChangeIt/Sites/mvo_server.py
---------------------
=====================
And restart apache.



=== HowTo Install a Python Package ===

The simplest way is to use easy_install by running:

sudo easy_install <package_name>.

If the package does not exists or if easy_install crashed you can install a
python package by downloading the sources and running:
=====================
---------------------
python setup.py build
python setup.py install --home $HOME
---------------------
=====================

You need to set the environment variable PYTHONPATH to $HOME/lib/python:
=====================
---------------------
export PYTHONPATH=$PYTHONPATH:$HOME/lib/python
---------------------
=====================

In 2.6 you can run:

=====================
---------------------
python setup.py install --user
---------------------
=====================
instead. No environment variable is needed.

== Usage ==

You can run a local server as:
=====================
---------------------
python ./src/multivio/dispatcher.py
---------------------
=====================

You can now access it at __http://localhost:4041__

== TODO ==

- error, message defintion for client/sever communication
- home made or existing http python framework

== Questions ==

- do I download a content file on the server even if I will not modify it
