# -*- coding: UTF-8 -*-
#input userid得到feature
import os

import torch
from transformers import BertTokenizer
from sklearn.preprocessing import LabelEncoder
import torch.nn.functional as F
import numpy as np

# 获得用户的特征向量 u

# 创建一个25维的向量来表示 user feature，根据user对一下25个topics（按字母排序）的喜欢程度（0-10）：
# autos, entertainment, finance, foodanddrink, health, lifestyle, movies, music, news_crime,
# news_others, news_politics, news_scienceandtechnology, news_world, sports_baseball,
# sports_basketball, sports_football, sports_golf, sports_icehockey, sports_mma-boxing,
# sports_others, sports_racing, travel, tv, video, weather
def blogrecommend(user,blogs):
    u = np.array(user)
    print(u)
    # u = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    # %%

    # 博客文本
    group_blogs = {
        0: 'These seemingly harmless habits are holding you back and keeping you from shedding that unwanted belly fat for good.',
        1: "Several fines came down against NFL players for criticizing officiating this week. It's a very bad look for the league.",
        2: "The 2019 Ram 3500's new Cummins diesel has 1000 lb-ft of torque. We put it to work on the drag strip.",
        3: "Every confirmed or expected PS5 game we can't wait to play",

        4: 'These seemingly harmless habits are holding you back and keeping you from shedding that unwanted belly fat for good.',
        5: "Several fines came down against NFL players for criticizing officiating this week. It's a very bad look for the league.",
        6: "The 2019 Ram 3500's new Cummins diesel has 1000 lb-ft of torque. We put it to work on the drag strip.",
        7: "Every confirmed or expected PS5 game we can't wait to play",

        8: 'These seemingly harmless habits are holding you back and keeping you from shedding that unwanted belly fat for good.',
        9: "Several fines came down against NFL players for criticizing officiating this week. It's a very bad look for the league.",
        10: "The 2019 Ram 3500's new Cummins diesel has 1000 lb-ft of torque. We put it to work on the drag strip.",
        11: "Several fines came down against NFL players for criticizing officiating this week. It's a very bad look for the league.",

        # 'id12': "The 2019 Ram 3500's new Cummins diesel has 1000 lb-ft of torque. We put it to work on the drag strip.",
        # 'id13': "Every confirmed or expected PS5 game we can't wait to play",
        # 'id14': 'These seemingly harmless habits are holding you back and keeping you from shedding that unwanted belly fat for good.',
        # 'id15': "Several fines came down against NFL players for criticizing officiating this week. It's a very bad look for the league.",
        # 'id16': "The 2019 Ram 3500's new Cummins diesel has 1000 lb-ft of torque. We put it to work on the drag strip.",
        # 'id17': "Every confirmed or expected PS5 game we can't wait to play",
        # 'id18': 'These seemingly harmless habits are holding you back and keeping you from shedding that unwanted belly fat for good.',
        # 'id19': "Several fines came down against NFL players for criticizing officiating this week. It's a very bad look for the league.",
        # 'id20': "The 2019 Ram 3500's new Cummins diesel has 1000 lb-ft of torque. We put it to work on the drag strip.",
        # 'id21': "Several fines came down against NFL players for criticizing officiating this week. It's a very bad look for the league.",
        # 'id22': "The 2019 Ram 3500's new Cummins diesel has 1000 lb-ft of torque. We put it to work on the drag strip.",
        # 'id23': "Every confirmed or expected PS5 game we can't wait to play",
        # 'id24': 'These seemingly harmless habits are holding you back and keeping you from shedding that unwanted belly fat for good.',
        # 'id25': "Several fines came down against NFL players for criticizing officiating this week. It's a very bad look for the league.",
        # 'id26': "The 2019 Ram 3500's new Cummins diesel has 1000 lb-ft of torque. We put it to work on the drag strip.",
        # 'id27': "Every confirmed or expected PS5 game we can't wait to play",
        # 'id28': 'These seemingly harmless habits are holding you back and keeping you from shedding that unwanted belly fat for good.',
        # 'id29': "Several fines came down against NFL players for criticizing officiating this week. It's a very bad look for the league.",
        # 'id30': "The 2019 Ram 3500's new Cummins diesel has 1000 lb-ft of torque. We put it to work on the drag strip.",

    }


    # 初始化Bert的tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    # 编码文本为token IDs和attention mask
    encoded_texts = [tokenizer.encode_plus(
        blog_text,
        add_special_tokens=True,
        max_length=512,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt'
    ) for blog_text in group_blogs.values()]

    # 将所有编码后的文本放在一个列表中
    input_ids = torch.cat([encoded_text['input_ids'] for encoded_text in encoded_texts], dim=0)
    attention_mask = torch.cat([encoded_text['attention_mask'] for encoded_text in encoded_texts], dim=0)

    # 将模型放到GPU上（如果有的话）
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 加载微调后的BERT模型
    path = os.path.abspath("v21_fine_tuned_bert_dense_classifier.pth")
    print(path)
    loaded_model = torch.load(path,map_location=torch.device('cpu'))  # 注意：加载微调后的模型！！
    loaded_model.to(device)

    # 推断所有文本（分类）
    with torch.no_grad():
        logits = loaded_model(input_ids.to(device), attention_mask=attention_mask.to(device))

    # 对模型的输出进行softmax操作以获取概率分布
    logits = logits.logits  # 访问logits字段
    probs = F.softmax(logits, dim=1)

    # 创建LabelEncoder并将类别标签编码为整数
    labels_list = ['news_crime', 'news_others', 'news_politics', 'news_scienceandtechnology', 'news_world',
                   'sports_racing', 'sports_others', 'sports_mma-boxing', 'sports_icehockey', 'sports_golf',
                   'sports_basketball', 'sports_football', 'sports_baseball', 'autos', 'finance',
                   'entertainment', 'foodanddrink', 'health', 'lifestyle', 'travel',
                   'movies', 'music', 'tv', 'video', 'weather']

    label_encoder = LabelEncoder()
    labels_encoded = label_encoder.fit_transform(labels_list)

    # 获取每个类别的可能性概率
    class_probabilities = probs.cpu().numpy()

    # 计算得分
    scores = np.dot(class_probabilities, u)

    # 创建一个字典，将博客ID与其分数关联起来
    blog_scores = {key: score for key, score in zip(group_blogs.keys(), scores)}

    print(blog_scores)

    # 取出前k个最大score对应的 blog id

    # 将字典 blog_scores 中的元素按其值从大到小排序，使用 sorted 函数并指定 reverse=True
    sorted_blog_scores = dict(sorted(blog_scores.items(), key=lambda item: item[1], reverse=True))
    #print(sorted_blog_scores)

    k = 2 #根据修改
    results = {}

    top_k_keys = list(sorted_blog_scores.keys())[:k]
    print(f"Top {k} keys with highest scores:")
    for key in top_k_keys:
        print(f"Blog ID: {key}, Score: {sorted_blog_scores[key]}")
        results[key] = sorted_blog_scores[key]
    print(list(results.keys()))
    return list(results.keys())


# import torch
# from transformers import BertTokenizer
# from sklearn.preprocessing import LabelEncoder
# import torch.nn.functional as F
#
# # %%
# # 获得用户的特征向量 u
# import numpy as np
#
# # 创建一个25维的向量来表示 user feature，根据user对一下25个topics（按字母排序）的喜欢程度（0-10）：
# # autos, entertainment, finance, foodanddrink, health, lifestyle, movies, music, news_crime,
# # news_others, news_politics, news_scienceandtechnology, news_world, sports_baseball,
# # sports_basketball, sports_football, sports_golf, sports_icehockey, sports_mma-boxing,
# # sports_others, sports_racing, travel, tv, video, weather
#
# u = np.array([1, 2, 0, 4, 7, 6, 7, 1, 9, 3, 5, 6, 9, 0, 10, 5, 8, 8, 3, 9, 10, 2, 3, 6, 5])
#
# # u = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
#
# # %%
#
# # 创建一个空的字典 dict_blogs，用于存储从user的groups中获得的blogs（从database读取，并存在字典group_blogs中）
# dict_blogs = {}
#
# # 将 group_blogs 赋值给 dict_blogs
# # 假设group_blogs是从user的groups中获得的blogs；id = blog's id in database，text = blog's content
# group_blogs = {
#     'id0': 'These seemingly harmless habits are holding you back and keeping you from shedding that unwanted belly fat for good.',
#     # 标签health
#     'id1': "Several fines came down against NFL players for criticizing officiating this week. It's a very bad look for the league. ",
#     # sports
#     'id2': "The 2019 Ram 3500's new Cummins diesel has 1000 lb-ft of torque. We put it to work on the drag strip.",
#     # autos
#     'id3': "Every confirmed or expected PS5 game we can't wait to play"}  # entertainment
#
# dict_blogs = group_blogs  # 将 group_blogs 赋值给 dict_blogs
#
# # 使用循环将字典 dict_blogs 中的值赋值给 blog_text，并使用分类器对其进行分类以及计算类别概率向量b，然后计算得分 score = b*u
#
# # 创建一个空的字典用于存储得分 id：score
# blog_scores = {}
#
# for key, value in dict_blogs.items():  # key即id，value即blog
#
#     # 创建一个变量 blog_text，并使用[key]来获取dict_blogs中的 value(即blog)
#     blog_text = dict_blogs[key]
#
#     # ————————————————————————————————————————
#     # 初始化Bert的tokenizer
#     tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
#
#     # 编码文本为token IDs和attention mask
#     encoded_text = tokenizer.encode_plus(
#         blog_text,
#         add_special_tokens=True,
#         max_length=512,
#         padding='max_length',
#         truncation=True,
#         return_attention_mask=True,
#         return_tensors='pt'
#     )
#
#     # 将模型放到GPU上（如果有的话）
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#
#     # 加载微调后的BERT模型
#     loaded_model = torch.load('G:\\Project\\Hotsearch_new\\Hotsearch_recommend\\v21_fine_tuned_bert_dense_classifier.pth',map_location=torch.device('cpu'))  # 注意：加载微调后的模型！！
#     loaded_model.to(device)
#
#     # ————————————————————————————————————————
#     # 推断文本（分类）
#     input_ids = encoded_text['input_ids'].to(device)
#     attention_mask = encoded_text['attention_mask'].to(device)
#     with torch.no_grad():
#         logits = loaded_model(input_ids, attention_mask=attention_mask)
#
#     # 对模型的输出进行softmax操作以获取概率分布
#     logits = logits.logits  # 访问logits字段
#     probs = F.softmax(logits, dim=1)
#
#     # 创建LabelEncoder并将类别标签编码为整数（确保labels_list包含训练时使用的标签）
#     labels_list = ['news_crime', 'news_others', 'news_politics', 'news_scienceandtechnology', 'news_world',
#                    'sports_racing', 'sports_others', 'sports_mma-boxing', 'sports_icehockey', 'sports_golf',
#                    'sports_basketball', 'sports_football', 'sports_baseball', 'autos', 'finance',
#                    'entertainment', 'foodanddrink', 'health', 'lifestyle', 'travel',
#                    'movies', 'music', 'tv', 'video', 'weather']
#
#     label_encoder = LabelEncoder()
#     labels_encoded = label_encoder.fit_transform(labels_list)
#
#     # ————————————————————————————————————————
#     # 获取每个类别的可能性概率
#     class_probabilities = probs[0].cpu().numpy()
#
#     # 获取类别标签
#     unique_categories = label_encoder.classes_
#
#     # 创建字典，将类别标签与其可能性概率关联起来
#     category_probabilities = {category: probability for category, probability in
#                               zip(unique_categories, class_probabilities)}
#
#     # #打印该blog被分类为各类别的可能性概率
#     print("Category Probabilities:")
#     for category, probability in category_probabilities.items():
#         print(f"{category}: {probability:.4f}")
#
#     # 从有序字典中提取概率值
#     probability_values = list(category_probabilities.values())
#
#     # 将概率值转换为NumPy数组，得到类别概率向量 b
#     b = np.array(probability_values)
#
#     # 计算，并存储每条blog的得分score
#     score = np.dot(b, u)
#     blog_scores[key] = score  # 存储得分到blog_scores字典中
#
# print(blog_scores)