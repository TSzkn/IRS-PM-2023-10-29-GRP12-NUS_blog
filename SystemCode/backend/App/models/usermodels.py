# -*- coding: UTF-8 -*-
from App.exts import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telephone = db.Column(db.String(11), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    hsList = db.relationship('Hotsearch',backref='author')
    #这里的author实际是user对象 内置函数返回名字
    def __str__(self):
        return self.username

class User_profile(db.Model):
    __tablename__ = 'userprofile'
    id = db.Column(db.Integer,db.ForeignKey('user.id'), primary_key=True)
    entertainment = db.Column(db.Float,default = 1)
    finance= db.Column(db.Float, default = 1)
    foodanddrink= db.Column(db.Float, default = 1)
    health= db.Column(db.Float,default = 1)
    lifestyle = db.Column(db.Float, default = 1)
    movies = db.Column(db.Float,default = 1)
    music = db.Column(db.Float,default = 1)
    news_crime = db.Column(db.Float, default = 1)
    news_others = db.Column(db.Float,default = 1)
    news_politics= db.Column(db.Float,default = 1)
    news_scienceandtechnology = db.Column(db.Float,default = 1)
    news_world= db.Column(db.Float,default = 1)
    sports_baseball= db.Column(db.Float,default = 1)
    sports_basketball= db.Column(db.Float,default = 1)
    sports_football= db.Column(db.Float,default = 1)
    sports_golf= db.Column(db.Float,default = 1)
    sports_icehockey= db.Column(db.Float,default = 1)
    sports_boxing= db.Column(db.Float,default = 1)
    sports_others= db.Column(db.Float,default = 1)
    sports_racing= db.Column(db.Float,default = 1)
    travel= db.Column(db.Float,default = 1)
    tv= db.Column(db.Float,default = 1)
    weather= db.Column(db.Float,default = 1)
    autos= db.Column(db.Float,default = 1)
    video= db.Column(db.Float,default = 1)
    #all = db.Column(db.Float,default = 0)

class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(20), nullable=False)
    group_description = db.Column(db.String(255))

    # def __repr__(self):
    #     return str(self.id)

class Usergroup(db.Model):
    __tablename__ = 'usergroup'
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

