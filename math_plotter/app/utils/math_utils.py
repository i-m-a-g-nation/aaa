import numpy as np

def clean_asymptotes(x, y, threshold=None):
    """
    处理渐近线和突变点，避免在断点处错误连线。
    在斜率过大且发生符号剧变的地方插入 np.nan。
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    
    y_clean = np.copy(y)
    
    dy = np.diff(y_clean)
    dx = np.diff(x)
    
    dx[dx == 0] = 1e-12
    slope = dy / dx
    
    # 如果未指定 threshold，使用基于数据范围的自适应阈值
    if threshold is None:
        # 排除极大值干扰后计算 y 的动态范围
        valid_y = y[np.abs(y) < 1e6]
        if len(valid_y) > 0:
            y_range = np.max(valid_y) - np.min(valid_y)
            x_range = np.max(x) - np.min(x)
            if x_range == 0: x_range = 1e-12
            # 基础斜率的数百倍作为突变阈值
            threshold = max(100.0, (y_range / x_range) * 500)
        else:
            threshold = 1000.0

    jump_indices = np.where(np.abs(slope) > threshold)[0]
    
    for idx in jump_indices:
        y_clean[idx] = np.nan
        y_clean[idx+1] = np.nan
        
    return x, y_clean
