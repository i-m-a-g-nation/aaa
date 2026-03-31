# 修复画布自动缩放与初始化范围 Spec

## Why
当前，绘制函数时（特别是周期函数，如 `y=sin(x)`），如果使用全局采样，或者由于缺少显式的 X 轴/Y 轴范围限制，会导致 PyQtGraph 自动将视图放大以包容所有生成的数据点。这不仅造成卡顿，也不符合预期。我们需要：
1. 锁定或提供一个合理的初始视口范围（例如 x: [-10, 10], y: [-10, 10]）。
2. 在添加新曲线时，**不应该**让画布自动去适应整条曲线的范围，而是只在当前视图范围内进行采样和绘制。
3. 提供一个“一键恢复初始视图”的功能。

## What Changes
- 修改 `PlotCanvas` 的初始化逻辑，禁用数据改变时的自动缩放（AutoRange），并设定初始坐标范围。
- 在 `MainWindow` 的 UI 中增加一个“恢复初始视图”的按钮，连接到 `PlotCanvas` 的恢复视口范围的方法。
- 确保 `Evaluator` 中的采样逻辑始终基于当前的 `view_range`，而不是无限制的全局范围。

## Impact
- Affected code:
  - `app/plotting/canvas.py`
  - `app/ui/main_window.py`

## ADDED Requirements
### Requirement: 初始画布范围与恢复功能
The system SHALL provide a fixed initial view range for the canvas and a button to restore this view.

#### Scenario: 软件启动
- **WHEN** user starts the application
- **THEN** the canvas should display a fixed view range (e.g., x from -10 to 10, y from -10 to 10).

#### Scenario: 点击恢复按钮
- **WHEN** user clicks the "恢复初始视图" button
- **THEN** the canvas should immediately return to the fixed initial view range.

## MODIFIED Requirements
### Requirement: 绘图时不自动扩展视图
The system SHALL NOT automatically scale the view range to fit newly added curves if it causes performance issues or infinite expansion.

#### Scenario: 添加周期函数
- **WHEN** user inputs `y=sin(x)` and adds the function
- **THEN** the canvas remains at the current view range and only plots the function within this range, without auto-zooming out.