MKS
===

An experiment in Python: units that get out of the way

Essentially consists of a flexible wrapper around any object that keeps a
tally of units based on the operations performed on them.

To register the units into your current namespace,

>>> import MKS
>>> namespace = {} # ie. globals()
>>> MKS.define(namespace)

This makes the expected unit objects available without needing individual
initialization.

>>> length = 3 * m
>>> print( length )
3 m

Units can easily be cast to desired units, but this is up to the user.
MKS makes no effort to optimize prefixes.

>>> km = 1000 * m
>>> length(km)
0.003

Go wild!

Copyright (c) 2014, Roderic Day.
License: MIT (see LICENSE for details)
