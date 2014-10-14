from __future__ import division

BASE = {
    'L':'m',
    'M':'kg', 
    'T':'s',
    'I':'A',
    'O':'K',
    'N':'mol',
    'J':'cd',
}
DERIVED = {
    'LLM/ITTT': 'V',
    'LLM/TTT' : 'W',
    'LLM/TT'  : 'J',
    'LM/TT'   : 'N',
    'M/LTT'   : 'Pa',
    'IT'      : 'C',
}
CONSTANTS = {
    'R' : (8.3144621, 'MLL/NTTO'),
    'F' : (9.64853399E4, 'IT/N'),
}

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

    Perhaps a use-case for a metaclass
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
        >>> print Dimensions('M/N') + Dimensions('MT')
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
        all positives first, all negatives follow
        tiebreak alphabetically
        '''
        if str(self) in DERIVED:
            return DERIVED[str(self)]
        positive, negative = [], []
        for k in sorted(self, key=self.get):
            sym = BASE[k]
            exp = self[k]
            if self[k] > 0:
                if exp == 1:
                    positive.append("{}".format(sym))
                else:
                    positive.append("{}^{}".format(sym, exp))
            elif self[k] < 0:
                negative.append("{}^{}".format(sym, exp))
        return '.'.join(positive+negative[::-1])


class Measurement(object):
    '''
    Essentially a quantity/dimensions tuple, with all the magic that entails
    '''
    __array_priority__ = True

    def __init__(self, quantity, dimensions=''):
        if isinstance(quantity, type(self)):
            self.quantity = quantity.quantity
            self.dimensions = quantity.dimensions
        else:
            self.quantity = quantity
            self.dimensions = Dimensions(str(dimensions))

    def __eq__(self, other):
        other = Measurement(other)
        if self.dimensions != other.dimensions:
            raise UnitError(self.dimensions, other.dimensions)
        return self.quantity==other.quantity

    def __add__(self, other):
        other = Measurement(other)
        if self.dimensions != other.dimensions:
            raise UnitError(self.dimensions, other.dimensions)
        q = self.quantity + other.quantity
        d = self.dimensions
        return Measurement(q,d)

    def __neg__(self):
        return self*-1

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        other = Measurement(other)
        q = self.quantity * other.quantity
        d = self.dimensions + other.dimensions
        return Measurement(q, d)

    def __div__(self, other):
        return self * other**-1

    def __truediv__(self, other):
        return self.__div__(other)

    def __rmul__(self, other):
        '''
        absorbs multiplicant on the LHS into a measurement, assuming it is
        dimensionless to begin with
        '''
        return Measurement(self.quantity * other, self.dimensions)

    def __pow__(self, power):
        q = 1 if self.quantity==1 else self.quantity**power
        d = self.dimensions*power
        return Measurement(q, d)

    def __repr__(self):
        a = repr(self.quantity)
        b = self.dimensions
        return "Measurement({}, {})".format(a, b)

    def __str__(self):
        return "{} {}".format(self.quantity, self.dimensions.pretty).strip()

    def __or__(self, other):
        '''
        ensure that the dimensions match whatever is proposed, and return
        the scalar value. supposed to be the proper way to "exit" the unit
        process.
        '''
        other = Measurement(other)
        if self.dimensions != other.dimensions:
            raise UnitError(self.dimensions, other.dimensions)
        return self.quantity


def define(namespace):
    '''
    defines symbols in a given namespace
    '''
    variables = {}
    for dimensions, symbol in BASE.items()+DERIVED.items():
        if symbol in namespace:
            raise NameError('A variable {} already exists'.format(symbol))
        variables[symbol] = Measurement(1, dimensions)
    for symbol, (quantity, dimensions) in CONSTANTS.items():
        variables[symbol] = Measurement(quantity, dimensions)
    namespace.update(variables)


if __name__ == '__main__':
    import doctest, pytest
    doctest.testmod()
    pytest.main('tests.py')
