# encoding: utf-8
import pytest
pytest.main(__file__)

from MKS import define, Measurement, UnitError
define(globals())

def test_simplest():
    assert str( 3 * kg ) == '3 kg'

def test_correspondence():
    assert str( (2*m) * (2*m) ) == '4 m²'

def test_leading():
    assert str( 1 * 2*s * 3 ) == '6 s'

def test_repr():
    assert repr( 5 * kg * kg * s * s ) == 'Measurement(5, MMTT)'

def test_collect():
    assert str( 2 * s * s * kg ) == '2 kg.s²'

def test_pow():
    assert str( s**-1 ) == '1 s⁻¹'

def test_cancelout():
    assert str( 6 * m * m**-1 ) == '6'

def test_mulpow():
    assert str( 6 * m * s**-1 ) == '6 m.s⁻¹'

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
    assert str( 1 * kg / kg ) == '1'

def test_constants():
    T = 1 * K
    h = 1.22 * V
    a = 0.5
    2*a*F/(R*T)*h + 1

def test_somefloats():
    sub = 0.500000 * m + 1./5 * m - 0.7000 * m
    assert sub(m) == 0

def test_sort_order():
    assert str( kg * A**2 / cd / m**2 ) == '1 kg.A².cd⁻¹.m⁻²'

def test_subtract():
    assert str( kg - kg ) == '-0.0 kg'

def test_guarantee():
    r = 1 * m
    A = r**2
    with pytest.raises(UnitError):
        A(m)
    assert A(m**2) == 1

def test_fracpower():
    l = h = 3 * m
    A = l * h
    assert str( A**0.5 ) == '3.0 m'

def test_prettyderived():
    assert str( 1 * C ) == '1 C'

def test_compare():
    assert 2 * m > 1 * m

def test_compare_bad():
    with pytest.raises(UnitError):
        2 * m == 2 * kg
    with pytest.raises(UnitError):
        2 * m > 1 * kg

def test_compare_float():
    assert 3.45 * m == 3.45 * m

def test_quit_dless():
    d = m / m
    assert type( d ) != type( m )

def test_unitconv():
    um = 1E-6 * m
    r = 1.32E-5 * m
    assert str( r(um) ) == str( 13.2 )
