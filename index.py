"""阿里云函数计算入口文件"""
from app import app


def handler(environ, start_response):
    """FC HTTP触发器入口"""
    return app(environ, start_response)
