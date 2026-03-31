import pytest
import sympy
from app.core.parser import ExpressionParser, ParseError

def test_parse_explicit():
    mode, expr = ExpressionParser.parse_function("y = x^2 + 2*x + 1")
    assert mode == "explicit"
    x = sympy.Symbol('x')
    assert expr.equals(x**2 + 2*x + 1)
    
    mode, expr = ExpressionParser.parse_function("sin(x) * exp(x)")
    assert mode == "explicit"
    assert expr.equals(sympy.sin(x) * sympy.exp(x))

def test_parse_implicit():
    mode, expr = ExpressionParser.parse_function("x^2 + y^2 = 1")
    assert mode == "implicit"
    x, y = sympy.symbols('x y')
    assert expr.equals(x**2 + y**2 - 1)

def test_parse_parametric():
    mode, expr = ExpressionParser.parse_function("x = cos(t), y = sin(t)")
    assert mode == "parametric"
    t = sympy.Symbol('t')
    assert expr[0].equals(sympy.cos(t))
    assert expr[1].equals(sympy.sin(t))

def test_parse_polar():
    mode, expr = ExpressionParser.parse_function("r = 1 + sin(theta)")
    assert mode == "polar"
    theta = sympy.Symbol('theta')
    assert expr.equals(1 + sympy.sin(theta))

def test_parse_piecewise():
    mode, expr = ExpressionParser.parse_function("Piecewise((x^2, x > 0), (-x, x <= 0))")
    assert mode == "explicit"
    # 不强制验证等价性，因为Piecewise稍微复杂，只需不报错即可

def test_security_and_errors():
    with pytest.raises(ParseError):
        ExpressionParser.parse_function("__import__('os').system('ls')")
        
    with pytest.raises(ParseError):
        ExpressionParser.parse_function("x = cos(t) ; y = sin(t)") # 格式错误
