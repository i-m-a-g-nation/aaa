import json
from PySide6.QtGui import QColor

class StorageService:
    @staticmethod
    def save_project(file_path: str, functions: dict):
        data = []
        for func_id, model in functions.items():
            data.append({
                'id': model.id,
                'original_str': model.original_str,
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
            
        # 返回原始字符串列表，由外部重新调用 parser 以保证安全
        return data
