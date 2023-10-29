# -*- coding: UTF-8 -*-
from flask import Blueprint, jsonify ,request
from flask_restful import Resource, fields, marshal_with, Api, marshal,reqparse
from sqlalchemy import inspect

from App.models.hotsearmodels import *
from App.models.usermodels import User,User_profile,Group,Usergroup
from App.algorithm.recommend import blogrecommend
from App.algorithm.blogsort import blogsort



#类视图 CBV class based view
#视图函数 FBV Functional based view
search_bp = Blueprint('hotsearch',__name__)
api = Api(search_bp)


#传入 类型id
hs_parser = reqparse.RequestParser()
hs_parser.add_argument('userid',type=int,location='args',required=True)

#hs_parser.add_argument('page',type=int)

group_filed = {
    'groupId':fields.Integer(attribute= 'id' ),
    'groupName':fields.String(attribute='group_name'),
    'groupDescription':fields.String(attribute='group_description')
}
#展示用户所加入的所有group
class Groupapi(Resource):
    #两种数据转换方法 marshalwith
    def get(self):
        args = hs_parser.parse_args()
        userid = args.get('userid')
        print(userid)
        usergroups = Usergroup.query.filter(Usergroup.user_id == userid).all()
        groupids = [usergroup.group_id for usergroup in usergroups]
        groups = Group.query.filter(Group.id.in_(groupids)).all()
        print(groups)
        data = {
            'data':marshal(groups,group_filed),
            'status':200
        }
        return data #自定义类型必须序列化
'''
{
    'has_more':true
    'data:[]
    'return_count':8
}
'''
#自定义一个field属性，解决反向引用
class AuthorName(fields.Raw):
    def format(self, value):
        return value.username
#如果不加这一步 hotsearch.author返回的就是user对象

#trending页面 需要先拿到userid 然后获取groupid 再从group里面获取热搜
hs_fields = {
    'id': fields.Integer,
    'title':fields.String(attribute='title'),
    'desc':fields.String(attribute='abstract'),
    'datetime':fields.String(attribute='create_time'),
    'author':AuthorName(attribute='author'),
    # 'url':fields.Url('hotsearch.hsdetail',absolute=True)#点击响应后去看热搜具体信息 需要前端在title部分做一个超链接访问
    # #get方法会直接取 int：id
    # url这个部分需要蓝图进行操作 tmd没弄懂为啥
    #'comment':fields.Nested()  #评论不知道咋添加
    #fillder 模拟app抓包
}


# 获取某个热搜组下的所有热搜
class hslistapi(Resource):
    def get(self):
        args = hs_parser.parse_args()
        userid = args.get('userid')

        page = args.get('page',1)
        # hs_type = Searchtype.query.get(typeid)
        # 获取用户所在的group
        group = Usergroup.query.filter(Usergroup.user_id == userid).all()
        print(group)
        gp_list = []
        for gp in group:
            gp_list.append(gp.group_id)
        print(gp_list)
        hs_groups = Hsstore.query.filter(Hsstore.group_id.in_(gp_list)).all()
        print(list(hs_groups))
        #返回id值
        #获取对应group下的热搜
        idList = []
        clickList=[]
        timeList=[]
        hotList=[]
        for hs_gp in hs_groups:
            blog = Hotsearch.query.filter(Hotsearch.id == hs_gp.hs_id).first()
            idList.append(blog.id)
            clickList.append(blog.click_num)
            timeList.append(blog.create_time)
            hotList.append(0)

        #对获取到的热搜进行排序
        data={}
        data['id']=idList
        data['clicknum']=clickList
        data['createtime']=timeList
        data['hot']=hotList
        print('开始进行排序')
        sequence = blogsort(data)
        #得到热搜id list

        pagination = Hotsearch.query.filter(Hotsearch.id.in_(sequence)).paginate(page=page,per_page=8)
        data = {
            'has_more':pagination.has_next,
            'data':marshal(pagination.items,hs_fields),#存储的是hotsearch的id
            'return_count':len(pagination.items),
            'status':200
        }
        return data


hs_parser.add_argument('Blogid',type=int,location='args')
#展示热搜细节以及增加点击量
hs_detail_fields={
    'id':fields.Integer,
    'title':fields.String,
    'content':fields.String,
    'datetime':fields.String(attribute='create_time'),
    'clicknum':fields.Integer(attribute='click_num'),
    'author':AuthorName(attribute='author')
}
class HsDetailapi(Resource):

    def get(self):
        #更新该blog的点击量
        args = hs_parser.parse_args()
        userid = args.get('userid')
        id = args.get('Blogid')
        print(userid)

        hs = Hotsearch.query.filter(Hotsearch.id==id).first()
        hs.click_num += 1
        #
        # #获取对应tag
        print(User_profile)
        up = User_profile.query.filter(User_profile.id==userid).first()
        print(up)
        tags = hs.tags.split(',')
        print(up.__dict__.keys())
        for i in tags:
           up.__dict__[i] += 1
        db.session.commit()
        data = {
            'data': marshal(hs,hs_detail_fields),
            'status': 200
        }
        return data


#recommend 获取userid 然后groupid 然后得到group下的content，hsid以及user的信息之后处理完成返回hsid
class Hs_recommend(Resource):
    #算法
    def get(self):
        args = hs_parser.parse_args()
        userid = args.get('userid')
        page = args.get('page', 1)
        # 获取用户所在的group
        group = Usergroup.query.filter(Usergroup.user_id == userid).all()
        gp_list = []
        for gp in group:
            gp_list.append(gp.group_id)
        hs_group = Hsstore.query.filter(Hsstore.group_id.in_(gp_list)).all()
        print(hs_group)

        # 获取对应group下的热搜
        hs_list = []
        for hs in hs_group:
            hs_list.append(hs.hs_id)
        blogs = Hotsearch.query.filter(Hotsearch.id.in_(hs_list)).all()
        blog_content={}
        for blog in blogs:
            blog_content[blog.id] = blog.content
        #以上获取的是content
        #print(blog_content)
        #开始获取userfeature
        userprofile = User_profile.query.filter(User_profile.id == userid).first()
        attributes = dir(userprofile)
        # 遍历属性列表并输出属性名和对应的值 这里更改为点击数
        print('开始计算profile')
        inst = inspect(User_profile)
        attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
        print(attr_names)
        all = 0
        user_attribute={}
        for attribute in attr_names[1:]:
            value = getattr(userprofile, attribute)
            user_attribute[attribute] = value
            all += value
        # for attribute in attributes:
        #     value = getattr(userprofile, attribute)
        #     if isinstance(value, float):  # 仅输出浮点数属性
        #         user_attribute[attribute]=value
        #         all += value

        print(all)
        print(user_attribute)
        #计算userprofile百分数
        for attribute in attr_names[1:]:
            user_attribute[attribute]/=all
        print(user_attribute)
        #recommend需要给他一个user attribute以及相关的blog字典
        print('开始进行推荐算法')
        print(user_attribute.values())
        result = blogrecommend(list(user_attribute.values()),blog_content)
        #blog id content
        print(result)
        # blogre = Hotsearch.query.filter(Hotsearch.id.in_(result)).all()
        # data = {
        #     'data': marshal(blogre,hs_fields),
        #     'status': 200
        # }

        pagination = Hotsearch.query.filter(Hotsearch.id.in_(result)).paginate(page=page, per_page=8)
        data = {
            'has_more': pagination.has_next,
            'data': marshal(pagination.items, hs_fields),  # 存储的是hotsearch的id
            'return_count': len(pagination.items),
            'status': 200
        }
        return data

# class addClicknum(Resource):
#     def post(self):
#         args = hs_parser.parse_args()
#         hsid = args.get('id')
#         hs = Hotsearch.query.filter(hsid)

class Hs_latest(Resource):
    def get(self):
        args = hs_parser.parse_args()
        userid = args.get('userid')
        page = args.get('page',
                        1)
        # 获取用户所在的group
        group = Usergroup.query.filter(Usergroup.user_id == userid).all()
        gp_list = []
        for gp in group:
            gp_list.append(gp.group_id)
        hs_group = Hsstore.query.filter(Hsstore.group_id.in_(gp_list)).all()
        print(hs_group)
        hs_list = []
        for hs in hs_group:
            hs_list.append(hs.hs_id)

        pagination = Hotsearch.query.filter(Hotsearch.id.in_(hs_list)).paginate(page=page, per_page=8)
        data = {
            'has_more': pagination.has_next,
            'data': marshal(pagination.items, hs_fields),  # 存储的是hotsearch的id
            'return_count': len(pagination.items),
            'status': 200
        }
        return data




api.add_resource(Groupapi,'/gplist/')
api.add_resource(hslistapi,'/hslist')
api.add_resource(HsDetailapi,'/hsdetail')
api.add_resource(Hs_recommend,'/hsrecommend')
api.add_resource(Hs_latest,'/hslatest')
#id 热搜
#endpoint 管理具有相同类的两个或多个 url 时，必须指定 endpoint 参数

