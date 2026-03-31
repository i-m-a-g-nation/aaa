import numpy as np
import sympy
from skimage import measure
from app.utils.math_utils import clean_asymptotes

class Evaluator:
    @staticmethod
    def evaluate_explicit(expr, x_min, x_max, points=2000):
        x_sym = sympy.Symbol('x')
        # 兼容只包含常数的表达式，如 y = 5
        f = sympy.lambdify(x_sym, expr, modules=['numpy', 'scipy'])
        
        x_vals = np.linspace(x_min, x_max, points)
        try:
            y_vals = f(x_vals)
            # 如果 f 返回标量（如常数函数），转为数组
            if np.isscalar(y_vals):
                y_vals = np.full_like(x_vals, y_vals)
            
            x_vals, y_vals = clean_asymptotes(x_vals, y_vals)
            return x_vals, y_vals
        except Exception as e:
            return np.array([]), np.array([])

    @staticmethod
    def evaluate_parametric(expr_x, expr_y, t_min=0, t_max=2*np.pi, points=2000):
        t_sym = sympy.Symbol('t')
        fx = sympy.lambdify(t_sym, expr_x, modules=['numpy', 'scipy'])
        fy = sympy.lambdify(t_sym, expr_y, modules=['numpy', 'scipy'])
        
        t_vals = np.linspace(t_min, t_max, points)
        try:
            x_vals = fx(t_vals)
            y_vals = fy(t_vals)
            if np.isscalar(x_vals): x_vals = np.full_like(t_vals, x_vals)
            if np.isscalar(y_vals): y_vals = np.full_like(t_vals, y_vals)
            
            # 参数方程较少出现渐近线打断问题，但也可能存在，我们只过滤极值
            x_vals = np.where(np.abs(x_vals) > 1e6, np.nan, x_vals)
            y_vals = np.where(np.abs(y_vals) > 1e6, np.nan, y_vals)
            return x_vals, y_vals
        except Exception as e:
            return np.array([]), np.array([])

    @staticmethod
    def evaluate_polar(expr, theta_min=0, theta_max=2*np.pi, points=2000):
        theta_sym = sympy.Symbol('theta')
        f = sympy.lambdify(theta_sym, expr, modules=['numpy', 'scipy'])
        
        theta_vals = np.linspace(theta_min, theta_max, points)
        try:
            r_vals = f(theta_vals)
            if np.isscalar(r_vals):
                r_vals = np.full_like(theta_vals, r_vals)
                
            r_vals = np.where(np.abs(r_vals) > 1e6, np.nan, r_vals)
            
            x_vals = r_vals * np.cos(theta_vals)
            y_vals = r_vals * np.sin(theta_vals)
            return x_vals, y_vals
        except Exception:
            return np.array([]), np.array([])

    @staticmethod
    def evaluate_implicit(expr, x_min, x_max, y_min, y_max, resolution=200):
        x_sym, y_sym = sympy.symbols('x y')
        f = sympy.lambdify((x_sym, y_sym), expr, modules=['numpy', 'scipy'])
        
        x_vals = np.linspace(x_min, x_max, resolution)
        y_vals = np.linspace(y_min, y_max, resolution)
        X, Y = np.meshgrid(x_vals, y_vals)
        
        try:
            Z = f(X, Y)
            if np.isscalar(Z):
                return []
            
            # skimage.measure.find_contours 提取 Z=0 的等值线
            # 返回的是网格索引坐标 (row, col) = (y_idx, x_idx)
            contours = measure.find_contours(Z, 0.0)
            
            lines = []
            for contour in contours:
                # 转换回真实坐标
                # contour[:, 0] 是 row (对应 Y)，contour[:, 1] 是 col (对应 X)
                y_coords = y_min + contour[:, 0] / (resolution - 1) * (y_max - y_min)
                x_coords = x_min + contour[:, 1] / (resolution - 1) * (x_max - x_min)
                lines.append((x_coords, y_coords))
            return lines
        except Exception as e:
            return []
