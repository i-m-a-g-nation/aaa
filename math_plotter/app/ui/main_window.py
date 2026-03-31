from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox, QListWidget, QListWidgetItem, QMenuBar, QMenu, QFileDialog, QComboBox, QCheckBox
from PySide6.QtGui import QColor, QAction
from PySide6.QtCore import Qt

from app.core.parser import ExpressionParser, ParseError
from app.models.function_model import FunctionCurve
from app.plotting.canvas import PlotCanvas
from app.services.storage_service import StorageService
from app.services.export_service import ExportService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Math Plotter")
        self.resize(1000, 700)
        
        self.functions = {} # id -> FunctionCurve
        
        self._init_menu()
        self._init_ui()
        
    def _init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        
        save_action = QAction("保存工程", self)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        load_action = QAction("加载工程", self)
        load_action.triggered.connect(self.load_project)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("导出图片(PNG)", self)
        export_action.triggered.connect(self.export_image)
        file_menu.addAction(export_action)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧控制面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(300)
        
        # 输入区
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("例如: y = sin(x) 或 x^2+y^2=1")
        self.input_edit.returnPressed.connect(self.add_function)
        
        self.force_polar_cb = QCheckBox("作为极坐标绘制 (将 x 视为 θ)")
        
        self.add_btn = QPushButton("添加并绘制")
        self.add_btn.clicked.connect(self.add_function)
        
        left_layout.addWidget(QLabel("数学表达式:"))
        left_layout.addWidget(self.input_edit)
        left_layout.addWidget(self.force_polar_cb)
        left_layout.addWidget(self.add_btn)
        
        # 函数列表区
        left_layout.addWidget(QLabel("已添加的曲线:"))
        self.func_list = QListWidget()
        left_layout.addWidget(self.func_list)
        
        self.del_btn = QPushButton("删除选中")
        self.del_btn.clicked.connect(self.delete_function)
        left_layout.addWidget(self.del_btn)
        
        self.reset_btn = QPushButton("恢复初始视图")
        self.reset_btn.clicked.connect(lambda: self.canvas.reset_view())
        left_layout.addWidget(self.reset_btn)
        
        # 视图模式切换
        left_layout.addWidget(QLabel("背景网格模式:"))
        self.grid_mode_combo = QComboBox()
        self.grid_mode_combo.addItems(["直角坐标系网格", "极坐标系网格"])
        self.grid_mode_combo.currentIndexChanged.connect(
            lambda idx: self.canvas.set_grid_mode('cartesian' if idx == 0 else 'polar')
        )
        left_layout.addWidget(self.grid_mode_combo)
        
        # 点选信息显示区
        left_layout.addWidget(QLabel("点选信息:"))
        self.info_label = QLabel("暂无点选")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: blue;")
        left_layout.addWidget(self.info_label)
        left_layout.addStretch()
        
        # 右侧绘图区
        self.canvas = PlotCanvas()
        
        # 组装
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.canvas)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        # 信号连接
        self.canvas.view_changed.connect(self.redraw_all)
        self.canvas.point_clicked.connect(self.on_point_clicked)
        self.canvas.mouse_hovered.connect(self.on_mouse_hovered)

    def on_mouse_hovered(self, pos):
        self.statusBar().showMessage(f"当前坐标: x={pos[0]:.4f}, y={pos[1]:.4f}")

    def on_point_clicked(self, info):
        func_id = info['curve_id']
        func_model = self.functions.get(func_id)
        if not func_model:
            return
            
        text = f"曲线: {func_model.name}\n"
        text += f"x: {info['x']:.4f}\n"
        text += f"y: {info['y']:.4f}\n"
        
        if info.get('t') is not None:
            text += f"t: {info['t']:.4f}\n"
        if info.get('theta') is not None:
            text += f"θ: {info['theta']:.4f}\n"
            
        self.info_label.setText(text)

    def add_function(self):
        expr_str = self.input_edit.text()
        if not expr_str:
            return
            
        try:
            mode, parsed = ExpressionParser.parse_function(expr_str)
            
            # 如果用户勾选了强制极坐标，并且当前解析出来是 explicit (即 f(x))
            if self.force_polar_cb.isChecked() and mode == "explicit":
                import sympy
                # 将表达式中的 x 替换为 theta
                parsed = parsed.subs(sympy.Symbol('x'), sympy.Symbol('theta'))
                mode = "polar"
            
            # 分配随机颜色
            colors = [QColor(0, 114, 189), QColor(217, 83, 25), QColor(237, 177, 32), 
                      QColor(126, 47, 142), QColor(119, 172, 48), QColor(77, 190, 238)]
            color = colors[len(self.functions) % len(colors)]
            
            func_model = FunctionCurve(
                original_str=expr_str,
                parsed_expr=parsed,
                mode=mode,
                color=color,
                name=expr_str
            )
            
            self.functions[func_model.id] = func_model
            
            # 添加到 UI 列表
            item = QListWidgetItem(expr_str)
            item.setData(Qt.UserRole, func_model.id)
            # 设置文字颜色
            item.setForeground(color)
            self.func_list.addItem(item)
            
            # 绘制
            self.canvas.add_or_update_curve(func_model)
            self.input_edit.clear()
            
        except ParseError as e:
            QMessageBox.warning(self, "解析错误", str(e))
        except Exception as e:
            QMessageBox.critical(self, "系统错误", str(e))

    def delete_function(self):
        current_item = self.func_list.currentItem()
        if not current_item:
            return
            
        func_id = current_item.data(Qt.UserRole)
        if func_id in self.functions:
            del self.functions[func_id]
            self.canvas.remove_curve(func_id)
            
        self.func_list.takeItem(self.func_list.row(current_item))

    def redraw_all(self, view_range=None):
        for func_id, func_model in self.functions.items():
            self.canvas.add_or_update_curve(func_model)

    def save_project(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "保存工程", "", "JSON Files (*.json)")
        if file_path:
            try:
                StorageService.save_project(file_path, self.functions)
                QMessageBox.information(self, "成功", "工程保存成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def load_project(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "加载工程", "", "JSON Files (*.json)")
        if file_path:
            try:
                data = StorageService.load_project(file_path)
                # 清空当前
                self.functions.clear()
                self.canvas.clear_all()
                self.func_list.clear()
                
                for item_data in data:
                    expr_str = item_data['original_str']
                    mode, parsed = ExpressionParser.parse_function(expr_str)
                    func_model = FunctionCurve(
                        id=item_data['id'],
                        original_str=expr_str,
                        parsed_expr=parsed,
                        mode=mode,
                        color=QColor(item_data['color']),
                        width=item_data['width'],
                        visible=item_data['visible'],
                        name=item_data['name']
                    )
                    self.functions[func_model.id] = func_model
                    
                    list_item = QListWidgetItem(expr_str)
                    list_item.setData(Qt.UserRole, func_model.id)
                    list_item.setForeground(func_model.color)
                    self.func_list.addItem(list_item)
                    
                    self.canvas.add_or_update_curve(func_model)
                    
                QMessageBox.information(self, "成功", "工程加载成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载失败: {str(e)}")

    def export_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "导出图片", "", "PNG Files (*.png)")
        if file_path:
            try:
                ExportService.export_image(self.canvas.plot_widget, file_path)
                QMessageBox.information(self, "成功", "图片导出成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
