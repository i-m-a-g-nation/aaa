# 增加极坐标绘图支持与鼠标悬停坐标显示 Spec

## Why
目前软件已经部分实现了基于 Sympy 的极坐标解析 (`r=...`)，但用户提出明确需求要求“加上极坐标的绘图”，且“鼠标悬停在图像上能显示这一点的x,y值”。
我们需要确保极坐标函数的渲染链路完全打通，并在画布中添加鼠标悬停（Hover）事件，动态实时地显示当前鼠标所在位置的坐标。

## What Changes
1. **完善极坐标支持**：确保 `r = f(theta)` 形式的函数能够被正确解析、采样并在 PyQtGraph 画布中绘制为笛卡尔坐标系的线条。
2. **增加鼠标悬停事件（Hover）**：在 `PlotCanvas` 中监听鼠标移动事件，获取当前鼠标在画布中的场景坐标并映射到数据坐标 `(x, y)`。
3. **实时坐标显示**：在主界面增加一个用于显示当前鼠标悬停位置坐标的 UI 元素，通过信号槽机制实时更新。

## Impact
- Affected code:
  - `app/plotting/canvas.py`
  - `app/ui/main_window.py`

## ADDED Requirements
### Requirement: 鼠标悬停显示坐标
The system SHALL display the (x, y) coordinates of the current mouse position when the user hovers over the plot area.

#### Scenario: 鼠标在画布上移动
- **WHEN** user moves the mouse over the `PlotCanvas`
- **THEN** the UI updates a label to show the exact data coordinates `(x, y)` of the mouse cursor.

## MODIFIED Requirements
### Requirement: 极坐标绘图确认
The system SHALL fully support plotting polar coordinate functions (e.g., `r = 1 + cos(theta)`).

#### Scenario: 绘制极坐标函数
- **WHEN** user inputs `r = 1 + cos(theta)` and adds the function
- **THEN** the system successfully parses it, samples `r` and `theta`, converts them to `x` and `y`, and plots the curve correctly.