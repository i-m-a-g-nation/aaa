# Tasks

- [x] Task 1: 确保极坐标解析与渲染流程正常工作
  - **Description**: 当前代码中已经包含了 `ExpressionParser.parse_function` 对极坐标的解析，以及 `Evaluator.evaluate_polar` 的计算逻辑，还有 `canvas.py` 中的绘制代码。需要验证 `r = 1 + sin(theta)` 能否成功绘制。如果有任何断层，进行修复。
  - **Prompt**: Inspect `app/core/parser.py`, `app/core/evaluator.py`, and `app/plotting/canvas.py`. Verify that polar coordinates are properly evaluated and added to the canvas. No code changes might be necessary if it's already working, but ensure the data path is solid.

- [x] Task 2: 在 PlotCanvas 中添加鼠标悬停（Hover）事件监听
  - **Description**: 在 `app/plotting/canvas.py` 中，创建一个自定义的 `pyqtgraph.SignalProxy` 或者利用 `scene().sigMouseMoved` 来监听鼠标移动事件。当鼠标移动时，将屏幕坐标转换为数据坐标 (x, y)，并发出自定义信号 `mouse_hovered(tuple)`。
  - **Prompt**: Modify `app/plotting/canvas.py`. Add a `mouse_hovered = Signal(tuple)` to `PlotCanvas`. In `__init__`, connect `self.plot_widget.scene().sigMouseMoved` to a new method `_on_mouse_moved(self, pos)`. In `_on_mouse_moved`, check if `self.plot_widget.sceneBoundingRect().contains(pos)`, then map `pos` to view coordinates using `self.plot_widget.plotItem.vb.mapSceneToView(pos)` and emit `mouse_hovered.emit((mouse_point.x(), mouse_point.y()))`.

- [x] Task 3: 在主界面显示悬停坐标
  - **Description**: 在 `app/ui/main_window.py` 中，添加一个状态栏 (StatusBar) 或专门的 Label 用于显示实时悬停坐标。连接 `canvas.mouse_hovered` 信号到更新该 Label 的槽函数。
  - **Prompt**: Modify `app/ui/main_window.py`. In `_init_ui`, create a status bar using `self.statusBar()`. Connect `self.canvas.mouse_hovered` to a new method `on_mouse_hovered(self, pos)`. In this method, format the position as `f"当前坐标: x={pos[0]:.4f}, y={pos[1]:.4f}"` and set it as the status bar message using `self.statusBar().showMessage(text)`.

# Task Dependencies
- Task 3 depends on Task 2