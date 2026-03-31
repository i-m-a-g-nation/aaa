# 工程化与鲁棒性重构 Plan

## Summary
本项目需要进行一次深度的工程化与鲁棒性重构。当前应用能够运行，但在项目结构（入口文件路径注入）、表达式解析（简单的字符串切割和猜测）、运行时异常处理（静默吞掉异常）、性能（视图变化导致全量高代价重算）、交互细节（极坐标网格非自适应、KDTree频繁重建）以及状态持久化（丢失强制极坐标和范围配置等重要状态）上存在明显的脆弱点和缺陷。本计划将逐一解决这些问题，将项目从“原型状态”推向“专业的工程化状态”。

## Current State Analysis
1. **项目入口**: `app/main.py` 使用了 `sys.path.insert` 进行硬编码的路径注入。
2. **表达式解析 (`parser.py`)**: 
   - 依赖字符串特征（前缀、独立等号等）推断模式。
   - 参数方程使用简单的 `split(',')`，无法处理表达式内部（如 `Piecewise`）带有逗号的情况。
   - 虽然有关键字拦截，但底层使用 `eval` 驱动的 `parse_expr`。
3. **数值计算 (`evaluator.py`)**: 所有 `evaluate_*` 方法在捕获异常时都直接返回空数组，UI 无法获取失败原因。采样点数和渐近线阈值是写死的常量，缺乏基于视口的自适应。
4. **性能与渲染 (`canvas.py` & `main_window.py`)**: 
   - 视图改变 (`view_changed`) 会触发全量重算，对于隐函数或多曲线场景会导致严重卡顿。
   - KDTree 在每次点击时实时构建，且拾取距离使用数据坐标阈值，而不是屏幕像素阈值。
   - 极坐标网格范围写死，且在 `clear_all()` 时状态管理不完善。
5. **状态持久化 (`storage_service.py` & `FunctionCurve`)**: 仅保存了 `original_str`，丢失了 `mode`（特别是强制极坐标模式）、`t_min`、`t_max` 以及当前的 `grid_mode` 和 `view_range`。
6. **测试覆盖**: 缺乏对上述复杂边界条件（带有逗号的参数方程、保存/加载一致性、极坐标状态恢复等）的回归测试。

## Proposed Changes

### 1. 工程化项目结构 (Project Structure)
- **What**: 引入 `pyproject.toml`，将 `math_plotter` 注册为标准 Python 包。
- **Why**: 移除 `sys.path.insert` 的 hack，支持 `python -m math_plotter.app.main` 或 console script 启动，便于打包和 IDE 索引。
- **How**: 
  - 在根目录创建 `pyproject.toml`。
  - 移除 `app/main.py` 中的 `sys.path.insert` 逻辑。

### 2. 增强表达式解析器 (Robust Parser)
- **What**: 重写模式推断和参数方程拆分逻辑。
- **Why**: 解决带逗号的表达式被错误拆分的问题，使解析更加安全和健壮。
- **How**: 
  - 修改 `app/core/parser.py` 中的 `parse_function`。实现一个基于括号深度的智能 `split` 函数（`smart_split_parametric`），仅在括号层级为 0 时的逗号处进行切割。
  - 将模式 (`mode`) 从内部推断改为优先接受外部明确传入的 `mode`。

### 3. 细化运行时异常处理 (Error Handling)
- **What**: 定义具体的求值异常，并向上传递给 UI。
- **Why**: 避免静默失败，提供有意义的用户反馈。
- **How**: 
  - 在 `app/core/evaluator.py` 中抛出自定义的 `EvaluationError`（包含错误类型和原表达式）。
  - 在 `app/plotting/canvas.py` 和 `app/ui/main_window.py` 捕获该异常，通过 UI 提示或状态栏向用户报告“计算失败”或“数值越界”。

### 4. 自适应采样与性能优化 (Adaptive Evaluation & Performance)
- **What**: 根据视口动态调整采样率，并解耦平移与缩放的重算逻辑。
- **Why**: 减少卡顿，提高大范围缩放或拖拽时的流畅度。
- **How**: 
  - 修改 `app/core/evaluator.py`，允许传入动态的 `points` 和 `resolution`。
  - 在 `app/plotting/canvas.py` 中，如果只是小范围平移，考虑复用缓存数据（或仅做增量重算，第一步先实现简单的视口大小自适应采样数）。
  - 渐近线 `clean_asymptotes` 的 `threshold` 根据视口的 Y 轴范围动态计算。

### 5. 优化点击拾取与极坐标网格 (Interaction & Grid)
- **What**: 缓存 KDTree，改用屏幕像素阈值；动态绘制极坐标网格。
- **Why**: 提升点击性能和准确度；使极坐标网格在缩放时视觉自然，并修复状态重置 bug。
- **How**: 
  - `app/plotting/canvas.py`: 在每次生成/更新曲线数据时，预先构建并缓存 `cKDTree` 到 `self.curve_data_cache` 中。点击时使用映射到像素的距离进行判定。
  - 修改 `_draw_polar_grid`，使其根据当前的 `view_range` 动态决定同心圆的最大半径和密度。
  - 修复 `clear_all()`，确保清除后能根据当前的 `self.grid_mode` 正确恢复极坐标网格。

### 6. 完善工程持久化模型 (Storage & State Persistence)
- **What**: 扩展 JSON 存储的 Schema，包含缺失的语义状态。
- **Why**: 确保“保存 -> 加载”操作后，强制极坐标模式、参数范围和网格状态等不丢失。
- **How**: 
  - `app/services/storage_service.py` 和 `app/ui/main_window.py`: 在保存时写入 `mode`, `t_min`, `t_max`, `grid_mode` 和当前的 `view_range`。
  - 加载时，显式使用存储的 `mode` 进行解析和实例化，覆盖猜测逻辑，并恢复视图状态。

### 7. 补充回归测试 (Regression Tests)
- **What**: 编写针对新增工程逻辑和边界情况的测试。
- **Why**: 防止后续重构破坏现有逻辑。
- **How**: 
  - `tests/test_parser.py`: 增加测试 `Piecewise` 在参数方程中的解析。
  - `tests/test_storage.py`: 增加测试“保存后加载，`force_polar` 语义一致”。
  - （可选）UI / Canvas 的简单集成测试。

## Assumptions & Decisions
- 放弃原有的完全依赖字符串猜测模式，允许存储和加载时明确指定函数模式。
- 考虑到 PyQtGraph 的架构，KDTree 缓存是提升拾取性能的最佳性价比方案。
- `pyproject.toml` 采用标准的 `setuptools` 构建后端。

## Verification Steps
1. 运行 `pip install -e .`，然后通过 `python -m math_plotter.app.main` 成功启动。
2. 输入包含 `Piecewise` 的参数方程，验证能正确解析和绘制。
3. 输入一个会导致数学错误的表达式，验证 UI 能显示错误提示。
4. 绘制曲线，大幅缩放和平移，验证卡顿情况缓解且采样精度合理。
5. 在极坐标模式下保存工程，重启软件并加载，验证极坐标模式、网格和曲线完全恢复。
6. 运行所有 `pytest` 测试用例，确保全部通过。