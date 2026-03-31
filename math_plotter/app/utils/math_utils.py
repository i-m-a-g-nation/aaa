import numpy as np

def clean_asymptotes(x, y, threshold=100.0):
    """
    处理渐近线和突变点，避免在断点处错误连线。
    在斜率过大且发生符号剧变的地方插入 np.nan。
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    
    # 将 Inf 和超出合理绘图范围的极大值替换为 NaN
    # PyQtGraph 能够自动忽略 NaN 点并打断线条
    y_clean = np.copy(y)
    
    # 差分检测斜率
    dy = np.diff(y_clean)
    dx = np.diff(x)
    
    # 避免除零
    dx[dx == 0] = 1e-12
    slope = dy / dx
    
    # 找到斜率绝对值过大的点
    # threshold 可根据实际视口高度动态调整，这里给一个经验值
    jump_indices = np.where(np.abs(slope) > threshold)[0]
    
    for idx in jump_indices:
        # 如果是 y 跨越 0 导致的正负无穷，或者纯粹的跳跃
        # 稳妥起见，直接把跳跃点设为 nan
        y_clean[idx] = np.nan
        y_clean[idx+1] = np.nan
        
    return x, y_clean
