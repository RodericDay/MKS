__doc__ = '''An experiment in Python: units that get out of the way

Just a tuple wrapper that takes any object and exposes mathematical
methods while keeping a tally of units based on the operations
performed on them, and warning the user of restrictions accordingly.

The sophistication is minimal.

>>> road1 = 2 * km
>>> road2 = 500 * m
>>> path = road1 + road2
>>> speed = 10 * m / s
>>> time = path/speed
>>> ms = s / 1000
>>> time(ms)
250000

>>> P, V, n = atm, (0.3*m)**3, mol
>>> (P*V) // (n*R)
329 K

Copyright (c) 2014, Roderic Day.
License: MIT (see LICENSE for details)
'''

import functools

class UnitError(RuntimeError):
    pass

class Unit:
    order =   'I', 'J',  'L', 'M',  'N',   'O', 'T'
    symbols = 'A', 'cd', 'm', 'kg', 'mol', 'K', 's'
    known = {
        "Unit('IITTT', 'LLM')"   : 'S',
        "Unit('LLM', 'IITTT')"   : 'ohm',
        "Unit('LLM', 'ITTT')"    : 'V',
        "Unit('LLM', 'TTT')"     : 'W',
        "Unit('LLM', 'TT')"      : 'J',
        "Unit('LM', 'TT')"       : 'N',
        "Unit('M', 'LTT')"       : 'Pa',
        "Unit('IT', '')"         : 'C',
    }

    def __init__(self, n='', d=''):
        assert set(n+d).issubset(set(self.order))
        self.tally = [n.count(c)-d.count(c) for c in self.order]

    def __add__(self, other):
        '''
        >>> Unit('M', 'N') + Unit('MT')
        Unit('MMT', 'N')
        '''
        new = Unit()
        new.tally = [a+b for a, b in zip(self.tally, other.tally)]
        return new

    def __mul__(self, r):
        '''
        >>> Unit('MM', 'TT') * -0.5
        Unit('T', 'M')
        '''
        new = Unit()
        for i, n in enumerate(self.tally):
            m = n * r
            if not int(m)==m:
                raise UnitError("Power produces non-integer unit multiples")
            new.tally[i] = int(m)
        return new

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        '''
        >>> Unit('MM', 'T')
        Unit('MM', 'T')
        '''
        num = ''.join(c*( n) for c, n in zip(self.order, self.tally) if n > 0)
        den = ''.join(c*(-n) for c, n in zip(self.order, self.tally) if n < 0)
        return "Unit('{}', '{}')".format(num, den)

    def __str__(self):
        '''
        >>> print( Unit('MII', 'JLL') )
        kg.A².cd⁻¹.m⁻²
        >>> print( Unit('LLM', 'IITTT') )
        ohm
        '''
        if repr(self) in self.known:
            return self.known[repr(self)]
        d = str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻')
        it = sorted(zip(self.tally, self.symbols))
        # this gets the expected scientific format
        l = [s+str(e).translate(d) if e > 1 else s for e, s in it if e > 0]
        l+= [s+str(e).translate(d) for e, s in reversed(it) if e < 0]
        return '.'.join(l)

    def __eq__(self, other):
        return self.tally == other.tally


@functools.total_ordering
class Measurement:
    '''
    >>> m = Measurement(1, 'L')
    >>> s = Measurement(1, 'T')
    >>> (0.5 * m / s) ** -2
    4 s².m⁻²
    '''
    def __init__(self, quantity, unit):
        self.q = quantity
        if float(self.q).is_integer(): self.q = int(self.q)
        self.u = unit if isinstance(unit, Unit) else Unit(unit)

    def __rmul__(self, other):
        return Measurement(other * self.q, self.u)

    def __mul__(self, other):
        if isinstance(other, Measurement):
            return Measurement(self.q * other.q, self.u + other.u)
        # peel away unit layer if no units left
        new = Measurement(self.q * other, self.u)
        return new if str(new.u) else new.q

    def __add__(self, other):
        if self.u != other.u:
            raise UnitError("Addition requires unit match")
        return Measurement(self.q + other.q, self.u)

    def __pow__(self, e):
        return Measurement(self.q**e, self.u*e)

    def __repr__(self):
        return ' '.join([str(self.q), str(self.u)])

    def __gt__(self, other):
        if self.u != other.u:
            raise UnitError("Comparing different units not allowed")
        return self.q > other.q

    def __call__(self, other):
        value = self / other
        value = value if str(value.u) else value.q
        if isinstance(value, Measurement):
            raise UnitError("Unit mismatch", str(value) )
        return value

    def apply(self, f):
        self.q = f(self.q)
        return self if str(self.u) else self.q

    __floordiv__ = lambda self, other: (self/other).apply(int)
    __rtruediv__ = lambda self, other: other * self ** -1
    __truediv__ = lambda self, other: self * other ** -1
    __sub__ = lambda self, other: self + other * -1
    __eq__ = lambda self, other: self.u == other.u and self.q == other.q


namespace = globals()
# define all basic units
for u, name in zip(Unit.order, Unit.symbols):
    namespace[name] = Measurement(1, Unit(u))

# define known composite units
for form, name in Unit.known.items():
    namespace[name] = Measurement(1, eval(form))

# define constants
for name, value, num, den in [
    ('km' , 1E+3, 'L', ''),
    ('cm' , 1E-2, 'L', ''),
    ('mm' , 1E-3, 'L', ''),
    ('um' , 1E-6, 'L', ''),
    ('nm' , 1E-9, 'L', ''),
    ('mA' , 1E-3, 'I', ''),
    ('atm', 101325, 'M', 'LTT'),
    ('R'  , 8.3144621, 'MLL', 'NTTO'),
    ('F'  , 9.64853399E4, 'IT', 'N'),
    ('Av' , 6.02214129E23, '', 'N'),
    ('Da' , 1.660538921E-27, 'M', ''),
    ]: namespace[name] = Measurement(value, Unit(num, den))

if __name__ == '__main__':
    import doctest
    doctest.testmod(globs=globals())
