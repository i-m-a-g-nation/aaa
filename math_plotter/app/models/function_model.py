import uuid
from dataclasses import dataclass, field
from PySide6.QtGui import QColor

@dataclass
class FunctionCurve:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_str: str = ""
    parsed_expr: any = None
    mode: str = "explicit" # explicit, implicit, parametric, polar
    
    # 样式
    color: QColor = field(default_factory=lambda: QColor(0, 114, 189))
    width: int = 2
    visible: bool = True
    name: str = ""

    # 参数范围（仅用于 parametric 和 polar）
    t_min: float = 0.0
    t_max: float = 6.28318530718
    
    def __post_init__(self):
        if not self.name:
            self.name = self.original_str
