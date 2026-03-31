import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, QTimer
from app.core.evaluator import Evaluator, EvaluationError
from app.models.function_model import FunctionCurve
import numpy as np
from scipy.spatial import cKDTree

class PlotCanvas(QWidget):
    view_changed = Signal(tuple)
    point_clicked = Signal(dict) # 发射拾取到的点信息
    mouse_hovered = Signal(tuple) # 发射鼠标悬停的 (x, y) 坐标

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        pg.setConfigOptions(antialias=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('bottom', 'x')
        self.plot_widget.setLabel('left', 'y')
        
        # 禁用自动缩放，防止添加新曲线时视口无限扩展
        self.plot_widget.enableAutoRange(axis='xy', enable=False)
        self.plot_widget.setXRange(-10, 10, padding=0)
        self.plot_widget.setYRange(-10, 10, padding=0)
        
        self.layout.addWidget(self.plot_widget)
        
        self.curves = {}
        # 用于拾取的缓存数据：curve_id -> { 'x': array, 'y': array, 't': array/None }
        self.curve_data_cache = {} 
        
        # 防抖定时器
        self._view_change_timer = QTimer(self)
        self._view_change_timer.setSingleShot(True)
        self._view_change_timer.setInterval(200) # 200ms 防抖
        self._view_change_timer.timeout.connect(self._emit_view_changed)
        
        # 极坐标网格项
        self.polar_grid_items = []
        self.grid_mode = 'cartesian'
        
        self.plot_widget.sigRangeChanged.connect(self._on_view_change)
        self.plot_widget.scene().sigMouseClicked.connect(self._on_mouse_click)
        self.plot_widget.scene().sigMouseMoved.connect(self._on_mouse_moved)

    def set_grid_mode(self, mode: str):
        if mode == self.grid_mode:
            return
            
        self.grid_mode = mode
        if mode == 'cartesian':
            self.plot_widget.showGrid(x=True, y=True)
            for item in self.polar_grid_items:
                self.plot_widget.removeItem(item)
            self.polar_grid_items.clear()
        else:
            self.plot_widget.showGrid(x=False, y=False)
            self._draw_polar_grid()
            
    def _draw_polar_grid(self):
        # 绘制极坐标背景网格，根据视口大小动态调整
        view_range = self.get_view_range()
        max_extent = max(abs(view_range[0][0]), abs(view_range[0][1]), 
                         abs(view_range[1][0]), abs(view_range[1][1]))
        r_max = int(max_extent) + 2
        
        pen = pg.mkPen(color=(200, 200, 200), width=1, style=pg.QtCore.Qt.DashLine)
        
        # 决定同心圆的步长
        step = 1
        if r_max > 50: step = 5
        if r_max > 200: step = 20
        
        for r in range(step, r_max + 1, step):
            theta = np.linspace(0, 2 * np.pi, 200)
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            item = pg.PlotDataItem(x, y, pen=pen)
            item.setZValue(-10)
            self.plot_widget.addItem(item)
            self.polar_grid_items.append(item)
            
        for angle in range(0, 360, 30):
            rad = np.deg2rad(angle)
            x = [0, r_max * np.cos(rad)]
            y = [0, r_max * np.sin(rad)]
            item = pg.PlotDataItem(x, y, pen=pen)
            item.setZValue(-10)
            self.plot_widget.addItem(item)
            self.polar_grid_items.append(item)

    def _on_mouse_moved(self, pos):
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            self.mouse_hovered.emit((mouse_point.x(), mouse_point.y()))

    def _on_view_change(self):
        # 视图改变时，重启定时器
        self._view_change_timer.start()

    def _emit_view_changed(self):
        view_box = self.plot_widget.getViewBox()
        x_range = view_box.viewRange()[0]
        y_range = view_box.viewRange()[1]
        self.view_changed.emit((x_range[0], x_range[1], y_range[0], y_range[1]))

    def _on_mouse_click(self, event):
        if event.button() != 1: # 左键
            return
            
        pos = event.scenePos()
        if not self.plot_widget.sceneBoundingRect().contains(pos):
            return
            
        mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
        mx, my = mouse_point.x(), mouse_point.y()
        
        # 将鼠标位置映射回屏幕像素，以便使用像素距离进行拾取判定
        mouse_pixel = self.plot_widget.plotItem.vb.mapViewToScene(mouse_point)
        
        best_dist_pixel = float('inf')
        best_info = None
        
        for cid, data in self.curve_data_cache.items():
            if data.get('tree') is None:
                continue
            
            # 使用数据坐标查询最近点
            dist_data, idx = data['tree'].query([mx, my])
            
            # 取出该点，转换为屏幕像素计算真实距离
            pt_data = pg.QtCore.QPointF(data['x'][idx], data['y'][idx])
            pt_pixel = self.plot_widget.plotItem.vb.mapViewToScene(pt_data)
            
            # 屏幕像素距离
            dx = pt_pixel.x() - mouse_pixel.x()
            dy = pt_pixel.y() - mouse_pixel.y()
            dist_px = np.sqrt(dx**2 + dy**2)
            
            if dist_px < best_dist_pixel:
                best_dist_pixel = dist_px
                
                orig_idx = data['valid_mask'][idx]
                
                best_info = {
                    'curve_id': cid,
                    'x': data['x'][idx],
                    'y': data['y'][idx],
                    't': data['t'][idx] if data['t'] is not None else None,
                    'theta': data['theta'][idx] if data['theta'] is not None else None
                }
                
        # 屏幕像素阈值（例如 10 像素以内）
        if best_info and best_dist_pixel < 10.0:
            self.point_clicked.emit(best_info)

    def reset_view(self):
        """恢复初始坐标范围"""
        self.plot_widget.setXRange(-10, 10, padding=0)
        self.plot_widget.setYRange(-10, 10, padding=0)

    def get_view_range(self):
        view_box = self.plot_widget.getViewBox()
        return view_box.viewRange()

    def add_or_update_curve(self, func_model: FunctionCurve):
        self.remove_curve(func_model.id)
        if not func_model.visible:
            return
            
        view_range = self.get_view_range()
        x_min, x_max = view_range[0]
        y_min, y_max = view_range[1]
        
        padding_x = (x_max - x_min) * 0.1
        x_min -= padding_x
        x_max += padding_x
        
        pen = pg.mkPen(color=func_model.color, width=func_model.width)
        items = []
        
        cache_data = {'x': [], 'y': [], 't': None, 'theta': None}

        try:
            if func_model.mode == "explicit":
                x, y = Evaluator.evaluate_explicit(func_model.parsed_expr, x_min, x_max)
                if len(x) > 0:
                    item = pg.PlotDataItem(x, y, pen=pen, name=func_model.name)
                    items.append(item)
                    cache_data['x'] = x
                    cache_data['y'] = y
                    
            elif func_model.mode == "parametric":
                expr_x, expr_y = func_model.parsed_expr
                x, y = Evaluator.evaluate_parametric(expr_x, expr_y, func_model.t_min, func_model.t_max)
                if len(x) > 0:
                    item = pg.PlotDataItem(x, y, pen=pen, name=func_model.name)
                    items.append(item)
                    cache_data['x'] = x
                    cache_data['y'] = y
                    cache_data['t'] = np.linspace(func_model.t_min, func_model.t_max, len(x))
                    
            elif func_model.mode == "polar":
                x, y = Evaluator.evaluate_polar(func_model.parsed_expr, func_model.t_min, func_model.t_max)
                if len(x) > 0:
                    item = pg.PlotDataItem(x, y, pen=pen, name=func_model.name)
                    items.append(item)
                    cache_data['x'] = x
                    cache_data['y'] = y
                    cache_data['theta'] = np.linspace(func_model.t_min, func_model.t_max, len(x))
                    
            elif func_model.mode == "implicit":
                lines = Evaluator.evaluate_implicit(func_model.parsed_expr, x_min, x_max, y_min, y_max)
                all_x, all_y = [], []
                for lx, ly in lines:
                    item = pg.PlotDataItem(lx, ly, pen=pen)
                    items.append(item)
                    all_x.extend(lx)
                    all_y.extend(ly)
                if all_x:
                    cache_data['x'] = np.array(all_x)
                    cache_data['y'] = np.array(all_y)
        except EvaluationError as e:
            # 抛出给上层 UI 处理
            raise e

        # 构建并缓存 KDTree
        if len(cache_data['x']) > 0:
            pts = np.column_stack((cache_data['x'], cache_data['y']))
            valid_mask = ~np.isnan(pts).any(axis=1)
            if valid_mask.any():
                cache_data['tree'] = cKDTree(pts[valid_mask])
                cache_data['valid_mask'] = np.where(valid_mask)[0] # 记录原始索引
                # 为方便拾取反查，保留有效点的数据
                cache_data['x'] = cache_data['x'][valid_mask]
                cache_data['y'] = cache_data['y'][valid_mask]
                if cache_data['t'] is not None:
                    cache_data['t'] = cache_data['t'][valid_mask]
                if cache_data['theta'] is not None:
                    cache_data['theta'] = cache_data['theta'][valid_mask]

        for item in items:
            self.plot_widget.addItem(item)
            
        self.curves[func_model.id] = items
        self.curve_data_cache[func_model.id] = cache_data

    def remove_curve(self, curve_id):
        if curve_id in self.curves:
            for item in self.curves[curve_id]:
                self.plot_widget.removeItem(item)
            del self.curves[curve_id]
        if curve_id in self.curve_data_cache:
            del self.curve_data_cache[curve_id]

    def clear_all(self):
        self.plot_widget.clear()
        self.curves.clear()
        self.curve_data_cache.clear()
        self.polar_grid_items.clear()
        
        # 恢复网格状态
        if self.grid_mode == 'cartesian':
            self.plot_widget.showGrid(x=True, y=True)
        else:
            self.plot_widget.showGrid(x=False, y=False)
            self._draw_polar_grid()
