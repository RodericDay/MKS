from MKS import define, UnitError
import pytest

define(globals())

def test_simplest():
    assert str( 3 * kg ) == '3 kg'

def test_correspondence():
    assert str( (2*m) * (2*m) ) == '4 m^2'

def test_leading():
    assert str( 1 * 2*s * 3 ) == '6 s'

def test_repr():
    assert repr( 5 * kg * kg * s * s ) == 'Measurement(5, MMTT)'

def test_collect():
    assert str( 2 * s * s * kg ) == '2 kg.s^2'

def test_pow():
    assert str( s**-1 ) == '1 s^-1'

def test_cancelout():
    assert str( 6 * m * m**-1 ) == '6'

def test_mulpow():
    assert str( 6 * m * s**-1 ) == '6 m.s^-1'

def test_add():
    assert 6*m + 6*m == 12*m

def test_error():
    with pytest.raises(UnitError) as excinfo:
        6*m + 2*s
    assert str(excinfo.value) == UnitError.msg.format(m.dimensions, s.dimensions)

def test_ensurefloatdiv():
    assert str( 2*m*s / (4*m) ) == '0.5 s'

def test_defined():
    I = 1 * A
    assert V*I == J/s

def test_dimensionless():
    assert kg/kg + 1 == 2

def test_constants():
    T = 1 * K
    h = 1.22 * V
    a = 0.5
    2*a*F/(R*T)*h + 1

def test_somefloats():
    assert 0.500000 * m + 1./5 * m == 0.7000 * m

def test_sort_order():
    assert str( kg * A**2 / cd / m**2 ) == '1 kg.A^2.cd^-1.m^-2'

def test_subtract():
    assert str( kg - kg ) == '0 kg'

def test_guarantee():
    r = 1 * m
    with pytest.raises(UnitError):
        r**2 | m
    assert r**2 | m**2 == 1

def test_fracpower():
    l = h = 3 * m
    A = l * h
    assert str( A**0.5 ) == '3.0 m'

def test_prettyderived():
    assert str( 1 * C ) == '1 C'

if __name__ == '__main__':
    pytest.main(__file__)