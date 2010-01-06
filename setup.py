#!/usr/bin/env python
from distutils.core import setup

setup(
    name='multivio',
    version='0.0.1b',
    description='Multivio server.',
    long_description='''Multivio is a project...''',
    license='Internal',
    author='Johnny Mariethoz',
    author_email='Johnny do Mariethoz at rero do ch',
    url='http://www.multivio.org',
    packages=[
    'multivio'
    ],
    scripts=[
    'tools/multivio_server.py'
    ],
    keywords=['multivio'],
    classifiers=[
    'Development Status :: Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: Internal',
    ],
    )
