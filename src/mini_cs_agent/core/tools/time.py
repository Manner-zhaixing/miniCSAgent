'''
内置工具：获取当前时间
'''
from datetime import datetime

from langchain.tools import tool

@tool
def get_current_time() -> str:
    """获取当前系统时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    