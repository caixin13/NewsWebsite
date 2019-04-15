import logging
from logging.handlers import RotatingFileHandler

import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import config_dict


# 创建SQLAlchemy对象
db = SQLAlchemy()
redis_store = None

def setup_logging(log_level):
    """日志相关配置"""
    # 设置日志的记录等级
    logging.basicConfig(level=log_level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

def create_app(config_name):
    """通过传入不同的配置名字，初始化其对应配置的应用实例"""
    app = Flask(__name__)

    # 获取配置类
    config_cls = config_dict[config_name]

    # 加载项目配置信息
    app.config.from_object(config_cls)

    # db对象关联app
    db.init_app(app)

    # 创建redis链接对象
    global redis_store
    redis_store = redis.StrictRedis(host=config_cls.REDIS_HOST, port=config_cls.REDIS_PORT)

    # 为Flask项目开启CSRF保护
    CSRFProtect(app)

    # 创建Session对象
    Session(app)

    # 获取配置类
    config_cls = config_dict[config_name]

    # 项目日志配置
    setup_logging(config_cls.LOG_LEVEL)

    #注册蓝图
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    return app