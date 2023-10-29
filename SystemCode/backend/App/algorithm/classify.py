# -*- coding: UTF-8 -*-
import torch
from transformers import BertTokenizer
from sklearn.preprocessing import LabelEncoder
import torch.nn.functional as F
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def classify(question_text):
    # 读取用户输入的问题
    question_text = question_text
    # " The seemingly harmless habits are holding you back and keeping you from shedding that unwanted belly fat for good, right? "   # 问题标签 health

    # 初始化Bert的tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    # 编码文本为token IDs和attention mask
    encoded_text = tokenizer.encode_plus(
        question_text,
        add_special_tokens=True,
        max_length=512,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt'
    )

    # 将模型放到GPU上（如果有的话）
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 加载微调后的BERT模型
    loaded_model = torch.load('G:\\Project\Hotsearch_new\\Hotsearch_recommend\\v21_fine_tuned_bert_dense_classifier.pth',map_location=torch.device('cpu')) #注意：加载正确的模型！！
    loaded_model.to(device)

    # 推断文本（分类）

    input_ids = encoded_text['input_ids'].to(device)
    attention_mask = encoded_text['attention_mask'].to(device)

    with torch.no_grad():
        logits = loaded_model(input_ids, attention_mask=attention_mask)

    # 对模型的输出进行softmax操作以获取概率分布
    logits = logits.logits  # 访问logits字段
    probs = F.softmax(logits, dim=1)

    # 创建LabelEncoder并将类别标签编码为整数（确保labels_list包含训练时使用的标签）
    labels_list = ['news_crime','news_others','news_politics','news_scienceandtechnology','news_world',
                   'sports_racing','sports_others','sports_mma-boxing','sports_icehockey','sports_golf',
                   'sports_basketball','sports_football','sports_baseball','autos','finance',
                   'entertainment','foodanddrink','health','lifestyle','travel',
                   'movies','music','tv','video','weather']

    label_encoder = LabelEncoder()
    labels_encoded = label_encoder.fit_transform(labels_list)

    # 获取该问题被预测为各类别的概率
    class_probabilities = probs[0].cpu().numpy()

    # 获取类别标签
    unique_categories = label_encoder.classes_

    # 创建字典category_probabilities，将类别标签与其可能性概率关联起来
    category_probabilities = {category: probability for category, probability in zip(unique_categories, class_probabilities)}


    # 用sorted函数对category_probabilities字典按值从大到小进行排序
    sorted_output_dict = {k: v for k, v in sorted(category_probabilities.items(), key=lambda item: item[1], reverse=True)}

    # 打印排序后的字典
    print("Sorted Output Dictionary:")
    print(sorted_output_dict)

    # %%
    # 将字典category_probabilities中value值大于0.30（类别概率阈值）对应的key存在列表question_label中
    question_label = [k for k, v in category_probabilities.items() if v > 0.30]
    print(question_label)
    return question_label

def match(question,blog_dict):

    # 问题
    questions = []
    questions.append(question)
    #["who is the most handsome man in NUS?"]

    # 带ID的博客内容
    blogs = blog_dict
    print(blogs)
    blogs = {
        1: "Plus, an additional $750 off some vehicles in stock.",
        2: "Low Demand, Great Deals, High Quality: A Perfect Mix for Car Buyers",
        3: "With lots of these vehicles left on dealer lots, automakers will be eager to move them to driveways.",
        4: "As Jalopnik's resident car buying expert and professional car shopper, I get emails. Lots of emails. I've decided to pick a few questions and try to help out. This week we're talking about deceptive online pricing, finding a cheap car for a young driver, and also: What happens when you buy a car but it was sold to someone else?",
        5: "A new pilot program launching with 25 Porsche dealers will give potential owners a totally different purchasing experience.",
        6: "There are a lot of mistakes that buyers can make if they aren't careful that could end up costing them, including not understanding your budget or comparing deals. But the worst mistake. according to Edmunds, often comes after a savvy shopper closes their deal.",
        7: "It's probably not the most convenient, but it will get you the best deal. The post This Is the Best Time of the Week to Buy a Car appeared first on Reader's Digest.",
        8: "Zhang Kenan is the most handsome man in NUS."
    }

    # 创建DataFrame，带有文本和ID
    blog_df = pd.DataFrame(list(blogs.items()), columns=["id", "text"])

    # 初始化CountVectorizer和TfidfVectorizer
    count_vectorizer = CountVectorizer()
    tfidf_vectorizer = TfidfVectorizer()

    # 计算BOW向量
    bow_vectors = count_vectorizer.fit_transform(blog_df["text"])
    bow_vectors_q = count_vectorizer.transform(questions)

    # 计算TF-IDF向量
    tfidf_vectors = tfidf_vectorizer.fit_transform(blog_df["text"])
    tfidf_vectors_q = tfidf_vectorizer.transform(questions)

    # 计算问题与博客内容的余弦相似度
    cosine_similarities_bow = cosine_similarity(bow_vectors_q, bow_vectors)
    cosine_similarities_tfidf = cosine_similarity(tfidf_vectors_q, tfidf_vectors)

    # 获取博客ID
    blog_ids = blog_df["id"]

    # 计算相似度得分
    similarity_scores_bow = cosine_similarities_bow[0]
    similarity_scores_tfidf = cosine_similarities_tfidf[0]

    # 设置BOW和TF-IDF的权重（这里使用相等的权重，您可以根据需要进行调整）
    weight_bow = 0.3
    weight_tfidf = 0.8

    # 归一化余弦相似度
    normalized_cosine_bow = (similarity_scores_bow + 1) / 2
    normalized_cosine_tfidf = (similarity_scores_tfidf + 1) / 2

    # 计算加权和
    weighted_similarity_scores = (weight_bow * normalized_cosine_bow) + (weight_tfidf * normalized_cosine_tfidf)

    # # 计算加权和
    # weighted_similarity_scores = (weight_bow * similarity_scores_bow) + (weight_tfidf * similarity_scores_tfidf)

    # 创建包含ID和加权相似度得分的DataFrame
    weighted_similarity_df = pd.DataFrame({"id": blog_ids, "weighted_similarity": weighted_similarity_scores})

    # 按加权相似度得分降序排序
    sorted_weighted_similarity_df = weighted_similarity_df.sort_values(by="weighted_similarity", ascending=False)

    # 设定上下限
    upperlimit = 10
    floor = 5
    L = len(blogs) * 0.1
    T = 3
    T = 10 if L >10 else (3 if L < 3 else L)
    # 获取加权相似度最高的博客的ID
    most_similar_weighted_id = sorted_weighted_similarity_df.iloc[:T]["id"]

    # 打印排序后的加权相似度
    print("加权相似度排序：")
    print(sorted_weighted_similarity_df)

    # 打印加权相似度最高的博客的ID
    print("加权相似度最高的博客的ID：", most_similar_weighted_id)
    return most_similar_weighted_id