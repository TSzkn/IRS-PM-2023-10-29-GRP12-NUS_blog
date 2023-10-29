from random import random

from flask import Blueprint
from flask_restful import Api, Resource, reqparse, inputs
from ..models.usermodels import *
# user_bp = Blueprint('user',__name__)
# api = Api(user_bp)

#多个登录方式 帐户密码、第三方
#RequestParser  检验和转换请求数据
#发送手机验证码
# sms_parser = reqparse.RequestParser()
# #数据验证方法  1.验证参数名称   2.传递数据方式   3.验证参数的函数
# sms_parser.add_argument('mobile',location ='',type=inputs.regex(r'^1[356789]\d{9}$'),help='',required = True)
# class SendMessageapi(Resource):
#     def post(self):
#         args = sms_parser.parse_args()
#         mobile = args.get('mobile')

#==================================================

# lr_parser = reqparse.RequestParser()
# lr_parser.add_argument('mobile',location ='form',type=inputs.regex(r'^1[356789]\d{9}$'),help='手机号码格式错误',required = True)
#
# class Loginregisterapi(Resource):
#     def __pos__(self):
#         args = lr_parser.parse_args()
#         mobile = args.get('mobile')
#         #数据库查找是否存在此mobile
#         users = User.query.filter(User.telephone == mobile).all()
#         #判断列表
#         if users:
#             #登陆处理 记录登录状态 session cookie cache
#
#             pass
#         else:
#             #注册处理
#             user = User()
#             user.telephone = mobile
#             for i in range(13):
#                 ran = random.randint(0,9)
#             user.username = '用户'
#             pass

