#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='MKS',
    version='0.1.0',
    description="A unit system based on meter, kilo, and second",
    author='Roderic Day',
    author_email='roderic.day@gmail.com',
    url='www.permanentsignal.com',
    license='MIT',
)
