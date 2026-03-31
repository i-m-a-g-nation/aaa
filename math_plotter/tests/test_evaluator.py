import pytest
import numpy as np
import sympy
from app.core.evaluator import Evaluator

def test_evaluate_explicit():
    x = sympy.Symbol('x')
    expr = sympy.sin(x)
    x_vals, y_vals = Evaluator.evaluate_explicit(expr, 0, np.pi, 100)
    assert len(x_vals) == 100
    assert len(y_vals) == 100
    assert np.isclose(y_vals[0], 0)
    assert np.isclose(y_vals[-1], 0)

def test_evaluate_parametric():
    t = sympy.Symbol('t')
    expr_x = sympy.cos(t)
    expr_y = sympy.sin(t)
    x_vals, y_vals = Evaluator.evaluate_parametric(expr_x, expr_y, 0, 2*np.pi, 100)
    assert len(x_vals) == 100
    assert len(y_vals) == 100

def test_evaluate_polar():
    theta = sympy.Symbol('theta')
    expr = 1 + sympy.cos(theta)
    x_vals, y_vals = Evaluator.evaluate_polar(expr, 0, 2*np.pi, 100)
    assert len(x_vals) == 100
    assert len(y_vals) == 100

def test_evaluate_implicit():
    x, y = sympy.symbols('x y')
    expr = x**2 + y**2 - 1
    lines = Evaluator.evaluate_implicit(expr, -2, 2, -2, 2, 50)
    # 应能找到一个近似圆形的等值线集合
    assert len(lines) > 0
    # 测试线段中的点都在圆上 (误差范围内)
    for lx, ly in lines:
        for p_x, p_y in zip(lx, ly):
            assert np.abs(p_x**2 + p_y**2 - 1) < 0.2 # 由于分辨率问题，误差可能略大
