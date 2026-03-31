import json

class StorageService:
    @staticmethod
    def save_project(file_path: str, functions: dict, grid_mode: str, view_range: tuple):
        data = {
            'version': '1.1',
            'grid_mode': grid_mode,
            'view_range': view_range,
            'functions': []
        }
        for func_id, model in functions.items():
            data['functions'].append({
                'id': model.id,
                'original_str': model.original_str,
                'mode': model.mode, # 保存 mode 避免加载时重新猜测，丢失强制极坐标等状态
                't_min': model.t_min,
                't_max': model.t_max,
                'color': model.color.name(),
                'width': model.width,
                'visible': model.visible,
                'name': model.name
            })
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def load_project(file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 兼容旧版本 JSON (1.0)
        if isinstance(data, list):
            return {
                'version': '1.0',
                'grid_mode': 'cartesian',
                'view_range': None,
                'functions': data
            }
            
        return data
