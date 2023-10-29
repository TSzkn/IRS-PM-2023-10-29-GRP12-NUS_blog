# -*- coding: UTF-8 -*-
from datetime import datetime

from App.exts import db

class Chatbot(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer,db.ForeignKey('user.id'))
    history = db.Column(db.Text)
    role = db.Column(db.String(20))#判断是用户还是聊天机器人
    # 每次输入后 判断信息角色 并保存记录
    time = db.Column(db.DateTime, default=datetime.now)
