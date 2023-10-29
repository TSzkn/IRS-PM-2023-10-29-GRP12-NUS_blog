# -*- coding: UTF-8 -*-
#数据相关 数据库
from datetime import datetime
from App.exts import db
from .usermodels import User
#多对多 用户和热搜  用户和组群


class Hotsearch(db.Model):
    __tablename__ = 'hotsearch'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    abstract = db.Column(db.String(255),nullable = True)
    content = db.Column(db.Text, nullable=False)
    click_num = db.Column(db.Integer,nullable=False,default = 0)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    create_time = db.Column(db.DateTime, default=datetime.now)
    tags = db.Column(db.String(300),nullable = True)

    def __str__(self):
        return self.title

class Hsstore(db.Model):
    __tablename__ =  'hsstore'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hs_id = db.Column(db.Integer, db.ForeignKey('hotsearch.id'))
    group_id = db.Column(db.Integer,db.ForeignKey('group.id'))

    def __repr__(self):
        return str(self.hs_id)






