import os
import json
import pytest
from app.services.storage_service import StorageService
from app.models.function_model import FunctionCurve

def test_save_and_load_project(tmp_path):
    # 模拟数据
    func_model = FunctionCurve(
        id="test_id",
        original_str="y=x",
        mode="polar", # 强制极坐标模式
        t_min=0.0,
        t_max=10.0,
        name="test_func"
    )
    functions = {func_model.id: func_model}
    
    file_path = os.path.join(tmp_path, "test_proj.json")
    
    # 保存
    StorageService.save_project(file_path, functions, "polar", ((-5, 5), (-5, 5)))
    
    # 加载
    data = StorageService.load_project(file_path)
    
    assert data['version'] == '1.1'
    assert data['grid_mode'] == 'polar'
    # JSON 序列化 tuple 会变成 list
    assert data['view_range'] == [[-5, 5], [-5, 5]]
    
    func_data = data['functions'][0]
    assert func_data['id'] == "test_id"
    assert func_data['mode'] == "polar"
    assert func_data['t_max'] == 10.0
