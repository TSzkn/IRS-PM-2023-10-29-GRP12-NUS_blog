# -*- coding: UTF-8 -*-
import pandas as pd

def blogsort(data):
    # 创建一个字典，包含文章标题、点击量和时间的数据
    # data = {
    # 'id': ['文章1', '文章2', '文章3'],
    # 'clicknum': [100, 200, 150],
    # 'createtime': ['2023-01-01', '2023-01-02', '2023-01-03'],
    # 'hot': [0, 0, 0],
    # }
    print(data)
    # 使用Pandas创建DataFrame
    df = pd.DataFrame(data)

    # 打印DataFrame

    print(df)

    # 使用len()函数获取行数（文章数量）
    article_count = len(df)

    # 定义热度计算的权重
    clicks_weight = 0.6
    # 点击量权重
    time_weight = 0.4
    # 时间权重
    # 计算热度评分
    max_clicks = df['clicknum'].max()
    df['hot'] = (df['clicknum'] / max_clicks) * clicks_weight + (1 - df['createtime'].rank() / len(df)) * time_weight

    # 升序排序
    df_sorted = df.sort_values(by='hot', ascending=False)
    # 打印排序后的DataFrame
    print(df_sorted)

    # 提取排序后的文章标题
    sorted_article_titles = df_sorted['id']
    # 打印排序后的文章标题
    return sorted_article_titles