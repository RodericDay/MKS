# encoding: utf-8
from __future__ import division
import sys
python_version = sys.version_info[0]
import os, traceback

__all__ = [] # injected into namespaces by definition method call
__doc__ = '''An experiment in Python: units that get out of the way

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
'''

BASE = {
    'I':'A',
    'J':'cd',
    'L':'m',
    'M':'kg', 
    'N':'mol',
    'O':'K',
    'T':'s',
}
DERIVED = {
    'IITTT/LLM' : 'S',
    'LLM/IITTT' : 'ohm',
    'LLM/ITTT'  : 'V',
    'LLM/TTT'   : 'W',
    'LLM/TT'    : 'J',
    'LM/TT'     : 'N',
    'M/LTT'     : 'Pa',
    'IT'        : 'C',
}
CONSTANTS = {
    'atm': (101325, 'M/LTT'),
    'R'  : (8.3144621, 'MLL/NTTO'),
    'F'  : (9.64853399E4, 'IT/N'),
    'Da' : (1.660538921E-27, 'M'),
    'cm' : (1E-2, 'L'),
    'mm' : (1E-3, 'L'),
    'um' : (1E-6, 'L'),
    'nm' : (1E-9, 'L'),
    'mA' : (1E-3, 'I'),
}

reg =  '0123456789-'
sup = u'⁰¹²³⁴⁵⁶⁷⁸⁹⁻'
if python_version==3:
    SUP = {r: s for r, s in zip(reg, sup)}
else:
    SUP = {r: s.encode('utf-8') for r, s in zip(reg, sup)}


def superscript(integer):
    '''
    >>> print( superscript(-10) )
    ⁻¹⁰
    '''
    return ''.join([SUP[c] for c in str(integer)])

class UnitError(Exception):
    msg = "LHS had units <{}>, RHS had units <{}>."
    def __init__(self, L, R):
        self.L = L
        self.R = R
    def __str__(self):
        return self.msg.format(self.L, self.R)


class Dimensions(dict):
    '''
    A tally based on the SI system of units
    http://en.wikipedia.org/wiki/International_System_of_Units
    '''
    def __init__(self, string=''):
        self.update({k:0 for k in BASE.keys()})
        string = string.strip('1')
        if '/' in string:
            positive, negative = string.split('/')
        else:
            positive, negative = string, []
        for c in positive:
            self[c] += 1
        for c in negative:
            self[c] -= 1

    def __add__(self, other):
        '''
        >>> print( Dimensions('M/N') + Dimensions('MT') )
        MMT/N
        '''
        combination = Dimensions()
        for k in BASE.keys():
            combination[k] += self[k]
            combination[k] += other[k]
        return combination

    def __mul__(self, power):
        '''
        >>> Dimensions('M/T') * 2
        Dimensions('MM/TT')
        >>> Dimensions('T') * -3
        Dimensions('1/TTT')
        >>> Dimensions('M/T') * -1
        Dimensions('T/M')
        >>> Dimensions('MM/TT') * 0.5
        Dimensions('M/T')
        '''
        combination = Dimensions() + self
        for k in BASE.keys():
            v = combination[k] * power
            v == int(v) # no fractional units allowed
            combination[k] = int(v)
        return combination

    def __repr__(self):
        return "Dimensions('{}')".format(self)

    def __str__(self):
        '''
        >>> Dimensions('M/MT')
        Dimensions('1/T')
        '''
        top = ''.join(sorted(k*i for k,i in self.items() if i>0)) or '1'
        bottom = ''.join(sorted(k*(-i) for k,i in self.items() if i<0))
        frac = '/'.join([top, bottom]) if bottom else top
        return frac

    @property
    def pretty(self):
        '''
        prints out things in human-legible form
        order is positive ascending, negative descending

        >>> print( (A**2 / cd) * (kg / m**2) )
        1 kg.A².cd⁻¹.m⁻²
        '''
        if str(self) in DERIVED:
            return DERIVED[str(self)]
        positive, negative = [], []
        for k in sorted(self, key=self.get):
        # there's a bug involving lexicographic ordering
            sym = BASE[k]
            exp = self[k]
            if self[k] > 0:
                if exp == 1:
                    positive.append("{}".format(sym))
                else:
                    positive.append("{}{}".format(sym, superscript(exp)))
            elif self[k] < 0:
                negative.append("{}{}".format(sym, superscript(exp)))
        return '.'.join(positive+negative[::-1])


class Measurement(object):
    ''' A quantity/dimensions tuple, handling all tallying automatically
    behind the scenes.

    >>> length = 3 * m
    >>> print( length**2 )
    9 m²
    >>> print( 2 * length )
    6 m
    >>> print( 6 / s * m )
    6 m.s⁻¹
    >>> 3*m - 2*m == 1*m
    True
    >>> 6*m + 6*m == 12*m
    True
    >>> 2 * m < 1 * m
    False

    The object silently reverts back to a standard python object if units
    are cancelled out, which makes it simple to use exponentials and trig
    functions,

    >>> from math import exp
    >>> n = 1.2 * V
    >>> T = 300 * K
    >>> exp( F / (R * T) * n )
    1.442499337827071e+20

    Float division is assumed,

    >>> a, b = 2*m*s, 4*m
    >>> print( a / b )
    0.5 s

    '''
    __array_priority__ = True

    def __new__(cls, quantity, dimensions):
        ''' 
        if dimensionless, just return inner quantity object
        else, return tuple
        '''
        if str(dimensions)=='1':
            return quantity

        instance = object.__new__(cls)
        instance.__init__(quantity, dimensions)
        return instance

    def __init__(self, quantity, dimensions=''):
        if isinstance(quantity, type(self)):
            self.quantity = quantity.quantity
            self.dimensions = quantity.dimensions
        else:
            self.quantity = quantity
            self.dimensions = Dimensions(str(dimensions))

    def __call__(self, other):
        '''
        ensure that the dimensions match whatever is proposed, and return
        the scalar value. both the proper way to "exit" the unit process
        and a way to just test units at any point in code

        >>> (1 * m)(mm)
        1000.0
        '''
        out = self / other
        if hasattr(out, 'units'): # unit tuple shell was not discarded
            lunits = self.dimensions.pretty
            runits = other.dimensions.pretty if hasattr(other, 'units') else 1
            print( "Traceback (most recent call last):")
            for filepath, line_no, namespace, line in traceback.extract_stack():
                if os.path.basename(filepath)=='MKS.py': break
                print(  '  File "{filepath}", line {line_no}, in {namespace}\n'
                        '    {line}'.format(**locals()))
            print( 'ValueError: operands could not be broadcast together with units <{lunits}> <{runits}>'.format(**locals()) )
            exit()
        else:
            return out

    __len__ = lambda x: len(x.quantity)
    __abs__ = lambda x: Measurement(abs(x.quantity), x.dimensions)
    __neg__ = lambda x: x * -1
    __add__ = lambda x, o: ( x(o.units) + o(o.units) ) * o.units if hasattr(o, 'units') else x(o)
    __sub__ = lambda x, o: x + -o
    __eq__  = lambda x, o: x(o.units) == o(o.units)
    __lt__  = lambda x, o: x(o.units) <  o(o.units)
    __le__  = lambda x, o: x(o.units) <= o(o.units)
    __gt__  = lambda x, o: x(o.units) >  o(o.units)
    __ge__  = lambda x, o: x(o.units) >= o(o.units)
    __rdiv__= lambda x, o: o * x**-1
    __rtruediv__= lambda x, o: o * x**-1
    __iter__= lambda x: (v * x.units for v in x.quantity)

    def __rmul__(self, other):
        '''
        absorbs multiplicant on the LHS into a measurement, even if it is
        dimensionless to begin with
        '''
        return Measurement(self.quantity * other, self.dimensions)

    def __mul__(self, other):
        try:
            q = self.quantity * other.quantity
            d = self.dimensions + other.dimensions
        except AttributeError:
            q = self.quantity * other
            d = self.dimensions
        return Measurement(q, d)

    def __div__(self, other):
        return self.__truediv__(other)

    def __truediv__(self, other):
        return self * other**-1

    def __pow__(self, power):
        q = 1 if self.quantity is 1 else self.quantity**power
        d = self.dimensions*power
        return Measurement(q, d)

    def __repr__(self):
        a = repr(self.quantity)
        b = self.dimensions
        return "Measurement({}, {})".format(a, b)

    def __str__(self):
        return "{} {}".format(self.quantity, self.dimensions.pretty).strip()

    @property
    def label(self):
        '''
        returns a unicode label that ie: Matplotlib is able to handle
        '''
        return self.dimensions.pretty.decode('utf-8')

    @property
    def units(self):
        return Measurement(1, self.dimensions)

    def __getattr__(self, thing):
        if thing in ['sum','mean','min','max']:
            return lambda *a,**kw: getattr(self.quantity, thing)(*a,**kw) * self.units
        return getattr(super(Measurement, self), thing)

    def __hash__(self):
        '''
        Required if we are ever to use Measurement objects as keys.
        This is a poor implementation, and works badly.
        '''
        return 0


def define(namespace):
    '''
    defines symbols in a given namespace
    '''
    variables = {}
    for dimensions, symbol in list(BASE.items())+list(DERIVED.items()):
        if symbol in namespace:
            raise NameError('A variable {} already exists'.format(symbol))
        variables[symbol] = Measurement(1, dimensions)
    for symbol, (quantity, dimensions) in CONSTANTS.items():
        variables[symbol] = Measurement(quantity, dimensions)
    namespace.update(variables)


if __name__ == '__main__':
    namespace = globals()
    define(namespace)

    import doctest
    doctest.testmod(globs=namespace)

    # keep 1:1 between readme and docs for the meantime
    f = open('README.rst', 'r')
    if 'MKS\n' == next(f):
        f.close()
        f = open('README.rst', 'w')
        f.write("MKS\n===\n\n"+__doc__)
