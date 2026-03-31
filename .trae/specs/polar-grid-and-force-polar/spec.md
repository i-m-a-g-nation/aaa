# 极坐标网格与极坐标映射绘图 Spec

## Why
目前软件的底层绘图完全基于直角坐标系网格（Cartesian Grid），虽然可以通过 `r=f(theta)` 形式将极坐标转换为笛卡尔坐标画出图形，但：
1. 画布背景仍然是直角坐标系的方格（Grid），缺乏极坐标系的同心圆和放射线背景，视觉上不够“极坐标”。
2. 用户希望有一个开关/选项，能够强制将输入的**任何函数**（例如输入的 $y=f(x)$）直接作为极坐标下的 $r=f(\theta)$ 来进行映射绘制，以达到观察其在极坐标下形态的目的。

## What Changes
1. **画布坐标系切换功能**：在 `PlotCanvas` 中添加绘制极坐标网格（同心圆与角度射线）的功能。并在主界面提供“直角坐标系/极坐标系”的视图切换按钮或下拉框。
2. **强制极坐标映射**：在添加函数时，增加一个“强制作为极坐标绘制”的复选框。如果勾选，即使用户输入的是 $y=sin(x)$，系统也会在内部将其当作 $r=sin(\theta)$（把 $x$ 替换为 $\theta$，或者把 $y$ 视为 $r$）来采样并绘制。

## Impact
- Affected code:
  - `app/plotting/canvas.py` （添加背景网格切换）
  - `app/ui/main_window.py` （添加坐标系切换按钮、强制极坐标复选框）
  - `app/core/parser.py` / `app/core/evaluator.py` （可能需要稍微调整以支持强制替换自变量）

## ADDED Requirements
### Requirement: 极坐标网格背景
The system SHALL provide an option to switch the background grid from a Cartesian grid (squares) to a Polar grid (concentric circles and radial lines).

#### Scenario: 切换为极坐标视图
- **WHEN** user selects "极坐标系" view mode
- **THEN** the square grid is hidden, and concentric circles with radial lines are drawn on the canvas.

### Requirement: 强制极坐标映射
The system SHALL allow users to plot any explicit function $y=f(x)$ as a polar function $r=f(\theta)$.

#### Scenario: 强制极坐标绘图
- **WHEN** user inputs `y=x` and checks "作为极坐标绘制"
- **THEN** the system evaluates it as $r=\theta$ and plots an Archimedean spiral instead of a straight line.