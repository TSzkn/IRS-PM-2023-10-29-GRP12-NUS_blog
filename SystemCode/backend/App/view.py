# -*- coding: UTF-8 -*-
import json

from flask import Blueprint, request, redirect, url_for, session

from flask_restful import fields, marshal
from sqlalchemy import or_, inspect
from werkzeug.security import generate_password_hash, check_password_hash
from App.models.usermodels import *

user_bp = Blueprint('user',__name__)
user_filed = {
    'id':fields.Integer,
    'username':fields.String,
    'nickname':fields.String(attribute='nickname')

}

@user_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        pass
    else:
        # username = request.form.get('username')
        # password = request.form.get('password')
        username = request.json['username']
        password = request.json['password']
        print(username)
        print(password)
        print('!!!')
        user = User.query.filter(User.username==username).first()

        print(user)

        if user:
            #检查密码是否匹配
            flag = check_password_hash(user.password,password)
            # if user.password == password:
            #     flag=1
            if flag:
                print('登录成功')
                # response = redirect('hotsearch.hslistapi')
                # #或者改成 json数据anyway
                # #这个地方需要前端修改成get
                # response.set_cookie('username',user.username,max_age=1800)
                # session['user_id'] = user.id
                # 如果想在31天内都不需要登录
                #session.permanent = True
                data = {
                    'data':marshal(user, user_filed),
                    'status':200
                }
                return data
            else:

                return {
                    'errmsg':'手机号码或者密码错误，请确认好在登录',
                    'status':201
                }
        else:

            return {
                'errmsg':'该用户不存在',
                'status':202
            }


@user_bp.route('/regist/', methods=['GET', 'POST'])
def regist():
    if request.method == 'GET':
        pass
    else:
        username = request.json.get('username')
        nickname = request.json.get('nickname')
        password1 = request.json.get('password1')
        password2 = request.json.get('password2')
        telephone = request.json.get('telephone')

        # 手机号码验证，如果被注册了就不能用了
        user = User.query.filter(or_(User.telephone == telephone,User.username == username)).first()
        if user:
            return {
                'errmsg':'该手机号码被注册，请更换手机',
                'status':203
            }
        else:
            # password1 要和password2相等才可以
            if password1 != password2:
                return {
                    'errmsg':'两次密码不相等，请核实后再填写',
                    'status': 201
                }
            else:

                user = User()
                user.telephone=telephone
                user.username=username
                user.password=generate_password_hash(password1)
                user.nickname=nickname
                #添加到数据库
                db.session.add(user)
                db.session.commit()

                up = User_profile()
                # inst = inspect(User_profile)
                # attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
                up.id = user.id
                # for attribute in attr_names[1:]:
                #     up[attribute] = 1
                db.session.add(up)
                db.session.commit()
                # 如果注册成功，就让页面跳转到登录的页面,返回用户数据
                #return redirect(url_for('user.login'))
                data = {
                    'data':json.dumps(marshal(user, user_filed)),
                    'status':200
                }
                return data


#记录用户的登录状态


# 判断用户是否登录，只要我们从session中拿到数据就好了   注销函数
@user_bp.route('/logout/')
def logout():
    # session.pop('user_id')
    # del session('user_id')
    session.clear()
    data = {
        'msg':'登陆退出',
        'status':200
    }
    return data

from .models.hotsearmodels import *
group_filed = {
    'id':fields.Integer(attribute= 'id' ),
    'group_name':fields.String(attribute='group_name'),
    'group_description':fields.String(attribute='group_description')
}




#获取某个group的信息
@user_bp.route('/group', methods=['GET'])
def group():
    groupid = request.args.get('groupid')
    #page = args.get('page',1)
    # hs_type = Searchtype.query.get(typeid)
    print(groupid)
    group = Group.query.filter(Group.id == groupid).first()
    if group:
        data = {
            'data':marshal(group,group_filed),
            'status':200
        }
        print(data['data'])
    else:
        data={
            'errmsg':'该组不存在',
            'status':201
        }

    return data



#用户添加到某个组（在用户-组表里增加）
@user_bp.route('/uaddgroup/',methods = ['GET','POST'])
def useraddgroup():
    if request.method == 'POST':
        userid = request.json.get('userid')
        groupid = request.json.get('groupid')
        u = Usergroup.query.filter(Usergroup.user_id == userid,Usergroup.group_id == groupid).first()
        group = Group.query.filter(Group.id == groupid).first()
        if u:
            data = {
                'msg':'您已经加入过了',
                'status':200
            }
            return data
        else:
            up = Usergroup()
            up.user_id = userid
            up.group_id = groupid
            db.session.add(up)
            db.session.commit()
            data = {
                'data':marshal(group,group_filed),
                'status':200
            }
            return data


#用户自己创建（在用户-组表里增加，在group里增加）
@user_bp.route('/usercreate/',methods = ['GET','POST'])
def usercreate():
    if request.method=='POST':
        #添加新的group
        userid = request.json.get('userid')#后期全部用session搞定
        groupname = request.json.get('group_name')
        description = request.json.get('group_description')
        print(groupname)
        print(description)
        group = Group()
        group.group_name= groupname
        group.group_description = description
        db.session.add(group)
        db.session.commit()
        print('111')
        #usergroup表里更新
        up = Usergroup()
        up.user_id = userid
        # group = Group.query.
        up.group_id = group.id
        db.session.add(up)
        db.session.commit()
        data = {
            'data': marshal(group, group_filed),
            'status': 200
        }
        return data


