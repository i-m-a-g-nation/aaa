# Tasks

- [x] Task 1: 实现画布的极坐标网格背景绘制
  - **Description**: 在 `app/plotting/canvas.py` 中，添加一个方法 `set_grid_mode(self, mode)`，支持 "cartesian" 和 "polar"。在 "polar" 模式下，关闭原生的方形网格 `showGrid(x=False, y=False)`，并动态绘制一系列同心圆（使用 `pg.QtGui.QPainterPath` 或多个 `pg.PlotCurveItem`）和放射状直线。确保在缩放/平移时，极坐标网格能相对保持或重绘。由于动态极坐标网格较复杂，最简单的做法是在原点绘制几个固定半径的圆（如半径为 2, 4, 6, 8, 10...）和 12 条放射线。
  - **Prompt**: Modify `app/plotting/canvas.py`. Add a method `set_grid_mode(self, mode: str)`. If mode is 'cartesian', enable `showGrid(x=True, y=True)` and remove any polar items. If mode is 'polar', disable `showGrid(x=False, y=False)`. Create a group of `pg.PlotCurveItem` representing concentric circles (e.g., r=1 to 20) and radial lines (0 to 360 degrees step 30), style them with a light gray pen, and add them to `self.plot_widget`. Store these grid items in a list so they can be toggled.

- [x] Task 2: 在主界面增加“视图模式”切换
  - **Description**: 在 `app/ui/main_window.py` 中，增加一个 QComboBox，允许用户在“直角坐标系网格”和“极坐标系网格”之间切换，并连接到 `canvas.set_grid_mode`。
  - **Prompt**: Modify `app/ui/main_window.py`. In `_init_ui`, add a `QComboBox` for grid style selection with options "直角坐标系网格" and "极坐标系网格". Connect its `currentIndexChanged` signal to call `self.canvas.set_grid_mode('cartesian' if index==0 else 'polar')`.

- [x] Task 3: 增加“作为极坐标绘制”选项及解析逻辑调整
  - **Description**: 在 `app/ui/main_window.py` 输入框旁边加一个复选框 "作为极坐标绘制"。当勾选此项时，即使解析出是 explicit ($y=f(x)$)，也在创建 `FunctionCurve` 时将其强行转为极坐标模型，即将自变量替换为 $\theta$，并将其 `mode` 设为 `polar`。
  - **Prompt**: Modify `app/ui/main_window.py`. Add a `QCheckBox("作为极坐标绘制")` next to the input area. In `add_function()`, after calling `ExpressionParser.parse_function`, if the checkbox is checked, and the mode is `explicit`, change the mode to `polar` and replace the variable `x` with `theta` in the parsed expression using `parsed.subs(sympy.Symbol('x'), sympy.Symbol('theta'))`.

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 can be done in parallel