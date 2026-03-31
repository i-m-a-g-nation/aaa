import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import re

ALLOWED_NAMES = {
    'sin': sympy.sin, 'cos': sympy.cos, 'tan': sympy.tan,
    'cot': sympy.cot, 'sec': sympy.sec, 'csc': sympy.csc,
    'asin': sympy.asin, 'acos': sympy.acos, 'atan': sympy.atan,
    'sinh': sympy.sinh, 'cosh': sympy.cosh, 'tanh': sympy.tanh,
    'exp': sympy.exp, 'log': sympy.log, 'ln': sympy.log,
    'sqrt': sympy.sqrt, 'abs': sympy.Abs, 'sign': sympy.sign,
    'floor': sympy.floor, 'ceiling': sympy.ceiling,
    'pi': sympy.pi, 'E': sympy.E, 'e': sympy.E,
    'gamma': sympy.gamma, 'factorial': sympy.factorial, 'erf': sympy.erf,
    'Piecewise': sympy.Piecewise,
    'x': sympy.Symbol('x'), 'y': sympy.Symbol('y'),
    't': sympy.Symbol('t'), 'theta': sympy.Symbol('theta'),
    'r': sympy.Symbol('r')
}

# 必须提供 sympy 核心运算类，否则 parse_expr 会报 Add 未定义等错误
for name in ['Add', 'Mul', 'Pow', 'Integer', 'Float', 'Rational', 'Symbol', 'Eq', 'StrictGreaterThan', 'StrictLessThan', 'GreaterThan', 'LessThan', 'Gt', 'Lt', 'Ge', 'Le', 'Ne']:
    ALLOWED_NAMES[name] = getattr(sympy, name)

class ParseError(Exception):
    pass

class ExpressionParser:
    @staticmethod
    def _safe_parse(expr_str):
        expr_str = expr_str.replace('^', '**')
        # 拦截明显的危险关键字
        dangerous = ['__', 'import', 'eval', 'exec', 'sys', ';']
        for d in dangerous:
            if d in expr_str:
                raise ParseError("检测到非法关键字")
        
        # 对 os 关键字需要更小心的处理，防止误杀 cos, acos, cosh
        if re.search(r'\bos\b', expr_str):
            raise ParseError("检测到非法关键字 os")
            
        try:
            # 禁用内置函数
            g_dict = {"__builtins__": {}}
            parsed = parse_expr(
                expr_str,
                local_dict=ALLOWED_NAMES,
                global_dict=g_dict,
                transformations=standard_transformations + (implicit_multiplication_application,),
                evaluate=False
            )
            return parsed
        except Exception as e:
            raise ParseError(f"表达式解析失败: {str(e)}")

    @staticmethod
    def parse_function(input_str: str, mode: str = "auto"):
        input_str = input_str.strip()
        if not input_str:
            raise ParseError("输入不能为空")

        # 判断是否是真正的方程等号（排除 <=, >=, ==, !=）
        # 使用正则找独立的一个等号
        eq_match = re.search(r'(?<![<>!=])=(?![=])', input_str)

        if mode == "auto":
            if ',' in input_str and ('x=' in input_str.replace(' ','') or 'y=' in input_str.replace(' ','')):
                mode = "parametric"
            elif input_str.replace(' ', '').startswith('r='):
                mode = "polar"
            elif eq_match and not input_str.replace(' ', '').startswith('y='):
                mode = "implicit"
            else:
                mode = "explicit"

        if mode == "parametric":
            parts = input_str.split(',')
            if len(parts) != 2:
                raise ParseError("参数方程格式错误，应为 'x=f(t), y=g(t)'")
            
            x_str, y_str = parts[0].strip(), parts[1].strip()
            if x_str.startswith('y') and y_str.startswith('x'):
                x_str, y_str = y_str, x_str
            
            if not (x_str.startswith('x') and y_str.startswith('y')):
                raise ParseError("参数方程必须分别包含 x= 和 y=")
                
            x_expr_str = x_str.split('=', 1)[1]
            y_expr_str = y_str.split('=', 1)[1]
            
            x_expr = ExpressionParser._safe_parse(x_expr_str)
            y_expr = ExpressionParser._safe_parse(y_expr_str)
            return "parametric", (x_expr, y_expr)

        elif mode == "polar":
            if input_str.replace(' ', '').startswith('r='):
                expr_str = input_str.split('=', 1)[1]
            else:
                expr_str = input_str
            
            expr = ExpressionParser._safe_parse(expr_str)
            return "polar", expr

        elif mode == "implicit":
            if eq_match:
                idx = eq_match.start()
                left = input_str[:idx]
                right = input_str[idx+1:]
                left_expr = ExpressionParser._safe_parse(left)
                right_expr = ExpressionParser._safe_parse(right)
                expr = left_expr - right_expr
            else:
                expr = ExpressionParser._safe_parse(input_str)
            return "implicit", expr

        else: # explicit
            if input_str.replace(' ', '').startswith('y='):
                expr_str = input_str.split('=', 1)[1]
            else:
                expr_str = input_str
            
            expr = ExpressionParser._safe_parse(expr_str)
            return "explicit", expr
