# 日志配置的工具模块

import logging
import colorlog

# 初始化全局日志对象
logger = logging.getLogger()

# 设置日志的默认的级别
logger.setLevel(logging.INFO)

# 加载彩色日志处理器
handler = colorlog.StreamHandler()
# 定义日志输出的格式
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',  # INFO 显示为绿色
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))

# 应用日志配置信息
logger.addHandler(handler)

