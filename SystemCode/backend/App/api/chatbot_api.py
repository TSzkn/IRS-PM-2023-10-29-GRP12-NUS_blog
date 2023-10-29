# -*- coding: UTF-8 -*-
from flask import Blueprint
from flask_restful import Resource, Api
from flask import request
from App.models.usermodels import *
from App.models.hotsearmodels import *
from App.algorithm.classify import *




chatbot_bp = Blueprint('chatbot',__name__)
api = Api(chatbot_bp)

# hs_parser.add_argument('blog',type = str)
#在发送热搜时候 该热搜需要添加到对应组中

class Hsaddapi(Resource):
    #获取userid 从userid中获取groupid添加到热搜-group表
    def post(self):
        content = request.json.get('blog')
        userid = request.json.get('userid')
        abstarct = request.json.get('abstract')
        title = request.json.get('title')
        blog = Hotsearch()
        blog.content=content
        blog.user_id=userid
        blog.abstract=abstarct
        blog.title=title
        #添加文本分类
        #得到tags
        result=classify(content)
        tags = ','.join(result)
        blog.tags = tags
        #添加到hotsearch表
        db.session.add(blog)
        db.session.commit()
        #添加到hsstore表, blog对应的
        groups = Usergroup.query.filter(Usergroup.user_id==userid).all()
        groupids=[gp.group_id for gp in groups]
        stores=[]
        for i in groupids:
            hsstore = Hsstore()
            hsstore.group_id = i
            hsstore.hs_id=blog.id
            stores.append(hsstore)
        db.session.add_all(stores)
        db.session.commit()
        return {
            'msg': 'success',
            'status': 200
        }



#用chatbot进行提问 对问题打label 根据label选择数据库的blog
class chatapi(Resource):
    def post(self):
        question = request.json.get('question')
        userid = request.json.get('userid')
        #获取问题的类别
        tags = classify(question)
        print('给个结果')
        print(tags)
        blog_ids=[]
        if len(tags)>1:
            for i in tags:
                #按tag筛选符合要求的blog
                blogs = Hotsearch.query.filter(Hotsearch.tags.like('%{tag}%'.format(tag=i))).all()
                blog_id = [blog.id for blog in blogs]#单个tags
                blog_ids.extend(blog_id)
            blog_ids=list(set(blog_ids))#对blogid进行去重复
            blogAll = Hotsearch.query.filter(Hotsearch.id.in_(blog_ids)).all()
        else:
            blogAll = Hotsearch.query.filter(Hotsearch.tags.in_(tags)).all()

        #得到包含tag的所有blog
        blog_dict = {blog.id: blog.content for blog in blogAll}
        ids = match(question,blog_dict)
        print(ids)
        #准备给gpt的blog
        blogGpt = Hotsearch.query.filter(Hotsearch.id.in_(ids)).all()
        contentGpt = [blog.content for blog in blogGpt]
        print(contentGpt)
        data = {
            'data':contentGpt,
            'status': 200
        }
        return data




api.add_resource(Hsaddapi,'/hsadd/')
api.add_resource(chatapi,'/chatapi/')
