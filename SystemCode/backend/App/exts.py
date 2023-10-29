# -*- coding: UTF-8 -*-
#放置插件
#1.导包
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from flask_restful import Api

#2.初始化
db=SQLAlchemy()#orm 和类对应
migrate = Migrate()  #数据迁移 让模型（类）变成表
cors = CORS()

#3.和app对象绑定
def init_exts(app):
    #插件里基本都会有initapp方法
    db.init_app(app=app)
    migrate.init_app(app=app,db=db)
    cors.init_app(app,resources=r'/*', supports_credentials=True)
