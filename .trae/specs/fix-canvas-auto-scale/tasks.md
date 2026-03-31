# Tasks

- [x] Task 1: 设置画布初始范围与禁用自动缩放
  - **Description**: 在 `app/plotting/canvas.py` 中，初始化 `PlotWidget` 时，显式调用 `setXRange` 和 `setYRange` 设置初始范围为 [-10, 10]，同时禁用自动适应（auto range）功能，防止添加新曲线时视口乱跳。
  - **Prompt**: Modify `app/plotting/canvas.py`. In `PlotCanvas.__init__`, use `self.plot_widget.setXRange(-10, 10, padding=0)` and `self.plot_widget.setYRange(-10, 10, padding=0)`. Also disable auto-ranging on both axes using `self.plot_widget.enableAutoRange(axis='xy', enable=False)`. Add a `reset_view` method that reapplies these ranges.

- [x] Task 2: 优化视图重绘时的防抖(Debounce)与采样策略
  - **Description**: 当前 `_on_view_change` 会在视图改变的每一帧发出信号，导致重新采样和绘制，这会引起严重的卡顿。需要增加防抖机制。
  - **Prompt**: Modify `app/plotting/canvas.py`. Implement a QTimer to debounce the `sigRangeChanged` signal so that `self.view_changed.emit` is only called after the view has stopped changing for ~200ms. Also, verify that when `add_or_update_curve` is called, it correctly uses `x_min` and `x_max` based on the *current* view range rather than recalculating the whole domain. Note: ensure `QTimer` is properly imported from `PySide6.QtCore`.

- [x] Task 3: 在主界面增加“恢复初始视图”按钮
  - **Description**: 在 `app/ui/main_window.py` 左侧控制面板增加一个按钮，连接到 `PlotCanvas.reset_view`。
  - **Prompt**: Modify `app/ui/main_window.py`. In `_init_ui`, under the left layout, add a `QPushButton("恢复初始视图")` and connect its `clicked` signal to `self.canvas.reset_view`.

# Task Dependencies
- Task 3 depends on Task 1