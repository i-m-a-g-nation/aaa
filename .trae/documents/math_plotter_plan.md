# 阶段 1：需求细化与总体架构设计

## 1. 需求分析与支持/暂不支持范围

### 核心目标
开发一款基于 Python 的桌面端专业数学绘图软件，实现多种数学形式的解析、可视化和交互拾取，并具备保存/加载及图像导出等工程化能力。

### 支持范围
- **函数类型**：显函数 $y=f(x)$、参数方程 $x=f(t), y=g(t)$、极坐标 $r=f(\theta)$、隐函数 $F(x,y)=0$、分段函数。
- **数学能力**：基础四则运算、初等函数 (三角、对数、指数等)、常见特殊函数 (gamma, erf等)、常数 (pi, E)。
- **交互功能**：平移、缩放、重置视图、多图层管理、点击最近点拾取并显示详细坐标信息（笛卡尔/极坐标/参数值）。
- **工程化功能**：导出PNG、保存/加载JSON工程配置、深浅主题。

### 暂不支持范围
- 三维曲面绘图 (当前重点为2D专业绘图)。
- 复数域绘图 (所有计算结果约束在实数范围内)。
- 极其病态/高频震荡函数的无限保真 (如 $sin(1/x)$ 在 $x \to 0$ 处，采用截断和高密度采样，但不保证像素级绝对精确)。

## 2. 软件模块图与目录结构

采用 MVC/MVP 思想分离界面与核心逻辑，保证代码高可维护性。

```text
math_plotter/
├── requirements.txt
├── README.md
└── app/
    ├── main.py                  # 应用程序入口
    ├── ui/                      # GUI 层 (PySide6)
    │   ├── main_window.py       # 主窗口组装
    │   └── widgets/             # 子组件：输入区、图层管理、绘图容器、状态栏
    ├── core/                    # 核心计算与解析层
    │   ├── parser.py            # 基于 Sympy 的安全表达式解析引擎 (白名单机制)
    │   └── evaluator.py         # 数值计算与自适应采样逻辑
    ├── plotting/                # 绘图渲染层
    │   ├── canvas.py            # 封装 PyQtGraph 的绘图核心
    │   └── renderers.py         # 各类函数 (显/隐/极/参) 的渲染与更新策略
    ├── models/                  # 数据模型层
    │   ├── function_model.py    # 函数数据结构 (表达式、颜色、可见性、线宽等)
    │   └── project_model.py     # 工程整体状态 (多曲线集合、视口状态)
    ├── services/                # 外部交互与服务层
    │   ├── export_service.py    # 图像导出逻辑
    │   └── storage_service.py   # JSON 序列化/反序列化保存加载逻辑
    ├── utils/                   # 工具类
    │   ├── math_utils.py        # 渐近线检测、断点处理、KD-Tree最近点查询
    │   └── logger.py            # 全局日志配置
    └── tests/                   # 测试用例 (Pytest)
```

## 3. 核心数据流

1. **输入解析**：用户在 `ui.widgets.input_panel` 输入字符串表达式 $\rightarrow$ 传递给 `core.parser` $\rightarrow$ 使用 `sympy.parse_expr`（结合严格 `local_dict` 白名单）生成 Sympy AST 对象。
2. **构建模型**：解析成功后，将表达式对象和 UI 设置的样式参数打包为 `FunctionModel`，存入 `ProjectModel` 中。
3. **数值计算**：绘图引擎 `plotting.canvas` 获取当前视口边界 $[x_{min}, x_{max}]$ $\rightarrow$ 传递给 `core.evaluator`。
   - 显函数：利用 `sympy.lambdify` 生成 NumPy 向量化函数，计算 $y$ 数组。
   - 隐函数：在当前视口生成二维网格，计算 $Z = F(X,Y)$，通过 `skimage.measure.find_contours` (或类似 Marching Squares 算法) 提取等值线。
4. **渲染清洗**：`utils.math_utils` 对计算出的坐标数组进行清洗，识别并处理 NaN、Inf 以及突变点（渐近线打断），防止错误连线。
5. **交互响应**：数据传给 PyQtGraph 进行渲染。用户点击画布时，获取点击坐标 $\rightarrow$ 将当前显示曲线的顶点系构建 KD-Tree $\rightarrow$ O(logN) 查询最近点 $\rightarrow$ 反查点对应函数的数学参数并更新至 UI 状态栏/信息面板。

## 4. 关键类设计

- **`ExpressionParser`**: 负责将用户字符串转换为安全的 `sympy.Expr`，并识别函数类型（判断是隐函数、参数方程等）。
- **`FunctionCurve`**: 包含函数类型、原始表达式字符串、Sympy 对象、颜色 (`QColor`)、可见性、采样范围（针对极坐标/参数方程）等。
- **`PlotCanvas`**: 继承自 `pg.PlotWidget`，重写鼠标事件（Hover, Click），管理多个 `pg.PlotDataItem`。
- **`Evaluator`**: 核心计算类，提供 `evaluate_explicit(expr, x_range)`, `evaluate_parametric(expr_x, expr_y, t_range)` 等方法，返回清洗后的 `(x_array, y_array)`。

## 5. 技术选型与理由

- **GUI**: `PySide6`。理由：Python 现代桌面开发标配，组件丰富，与底层系统结合好。
- **数学解析**: `sympy`。理由：强大的计算机代数系统，避免手动编写危险的正则和 `eval`，天然支持海量数学函数和偏导计算。
- **数值计算**: `numpy` + `scipy`。理由：`numpy` 提供极致的向量化运算速度，`scipy` 提供 KD-Tree (拾取) 等高级功能。
- **绘图引擎**: `PyQtGraph`。理由：相比 `matplotlib`，`PyQtGraph` 与 Qt 结合更深，提供丝滑的高帧率交互体验（缩放、拖拽极度流畅）。
  - *针对隐函数的补充*：PyQtGraph 缺乏原生 `contour` 支持，我们将采用计算网格后利用 Marching Squares 算法提取线段坐标交由 PyQtGraph 绘制的方案，以保持底层交互体验的绝对统一，避免混合 `matplotlib` 导致的交互撕裂。
- **测试**: `pytest`。理由：语法简洁，易于编写数据驱动测试。

## 6. 潜在难点与解决策略

1. **安全性（恶意代码注入）**
   - **策略**：严格禁用 `eval`。使用 `sympy.parse_expr` 且 `evaluate=False`，配置自定义的 `local_dict` 白名单（仅包含 numpy/sympy 允许的数学符号和函数），彻底阻断系统命令执行可能。
2. **渐近线错误连线（如 $y=1/x$ 在 $x=0$ 处跨越正负无穷）**
   - **策略**：计算导数（差分），若相邻点 $\Delta y / \Delta x$ 超过设定阈值且发生符号剧变，则在两点间插入 `np.nan` 阻断画线。
3. **点选拾取算法的精度与性能**
   - **策略**：当画布上有数万个采样点时，线性查找太慢。每次曲线重绘后，在后台更新 `scipy.spatial.cKDTree`，点击时直接对鼠标的笛卡尔坐标执行近邻搜索，映射回原始数据索引，从而获得参数方程的 $t$ 或极坐标的 $\theta$。
4. **隐函数的渲染性能**
   - **策略**：隐函数计算量较大，拟采用动态分辨率策略。拖拽/缩放时使用低分辨率网格计算，鼠标释放后延迟（Debounce）几百毫秒再重新进行高密度网格计算和提取。

---
**下一阶段计划（第 2 阶段：项目骨架搭建）**
- 创建完整目录结构和 `requirements.txt`
- 搭建可启动的 PySide6 主窗口框架
- 实现基本的界面布局（左侧侧边栏、右侧画布）