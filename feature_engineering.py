#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/17 上午8:40
# @Author  : Zhizhou Li
# @File    : feature_engineering.py

import os
import re
import json
from typing import Dict, List
from collections import Counter

import jieba
import jieba.posseg as posseg
from tqdm import tqdm


def category_inspection(data: List[Dict[str, str]]):
    results = {}
    for item in tqdm(data):
        categories = item["category"]
        for category in categories:
            results[category] = results.get(category, 0) + 1
    return results


def sort_result_and_save(results: Dict[str, int], file_path: str):
    items = sorted(results.items(), key=lambda x: x[1], reverse=True)
    with open(file_path, 'w', encoding="utf-8") as wf:
        for pair in items:
            wf.write(pair[0] + ',' + str(pair[1]))
            wf.write('\n')


def search_content(data: List[Dict[str, str]], key: str, content: str):
    results = []
    for item in data:
        value = item[key]
        if content in value:
            results.append(item)
    return results


def regex_match_content(data: List[Dict[str, str]], content: str):
    results = []
    for item in data:
        value = item.get("body")
        if value:
            m = re.search(content, value)
            if m:
                results.append(item)
    return results


def cut_sentence(sample: Dict[str, str], grade: str = None):
    article = sample["body"]
    # pattern = re.compile(r".*?[。！？\(…{2}\)][”’》）]?")
    pattern = re.compile(r"[^!?。！？…]*\?[”’》）]?|[^!?。！？…]*![”’》）]?|[^!?。！？…]*。[”’》）]?|[^!?。！？…]*！[”’》）]?|[^!?。！？…]*？[”’》）]?|[^!?。！？…]*…{1,2}[”’》）]?")
    sentences = []
    paragraphs = [paragraph for paragraph in article.split('\n') if len(paragraph) > 0]
    for paragraph in paragraphs:
        paragraph_sentences = []
        double_quote_count = 0
        single_quote_count = 0
        book_title_count = 0
        parenthesis_count = 0
        temp_sentences = re.findall(pattern, paragraph.strip())
        for sentence in temp_sentences:
            paragraph_sentences.append(sentence)
            left_double_quotes = re.findall(r'“', sentence)
            right_double_quotes = re.findall(r'”', sentence)
            left_single_quotes = re.findall(r'‘', sentence)
            right_single_quotes = re.findall(r'’', sentence)
            left_book_title = re.findall(r'《', sentence)
            right_book_title = re.findall(r'》', sentence)
            left_parenthesis = re.findall(r'\(', sentence)
            right_parenthesis = re.findall(r'\)', sentence)
            double_quote_count = double_quote_count + len(left_double_quotes) - len(right_double_quotes)
            single_quote_count = single_quote_count + len(left_single_quotes) - len(right_single_quotes)
            book_title_count = book_title_count + len(left_book_title) - len(right_book_title)
            parenthesis_count = parenthesis_count + len(left_parenthesis) - len(right_parenthesis)
            if double_quote_count == 0 and single_quote_count == 0 and book_title_count == 0 and parenthesis_count == 0:
                sentences.append(''.join(paragraph_sentences))
                paragraph_sentences = []
    sentences = [{"id": sample["id"], "title": sample["title"], "category": sample["category"], "grade": grade, "sentence": sentence, "sequence_order": i} for i, sentence in enumerate(sentences)]
    return sentences


def regex_test(article: str):
    # pattern = re.compile(r".*?[。！？\(…\{\2\}\)][”’》）]?")
    # pattern = re.compile(r"(.*?。[”’》）]?)|(.*?！[”’》）]?)|(.*?？[”’》）]?)|(.*?…{1,2}[”’》）]?)")
    pattern = re.compile(r"[^!?。！？…]*\?[”’》）]?|[^!?。！？…]*![”’》）]?|[^!?。！？…]*。[”’》）]?|[^!?。！？…]*！[”’》）]?|[^!?。！？…]*？[”’》）]?|[^!?。！？…]*…{1,2}[”’》）]?")
    sentences = []
    paragraphs = [paragraph for paragraph in article.split('\n') if len(paragraph) > 0]
    for paragraph in paragraphs:
        paragraph_sentences = []
        double_quote_count = 0
        single_quote_count = 0
        book_title_count = 0
        parenthesis_count = 0
        temp_sentences = re.findall(pattern, paragraph.strip())
        for sentence in temp_sentences:
            paragraph_sentences.append(sentence)
            left_double_quotes = re.findall(r'“', sentence)
            right_double_quotes = re.findall(r'”', sentence)
            left_single_quotes = re.findall(r'‘', sentence)
            right_single_quotes = re.findall(r'’', sentence)
            left_book_title = re.findall(r'《', sentence)
            right_book_title = re.findall(r'》', sentence)
            left_parenthesis = re.findall(r'\(', sentence)
            right_parenthesis = re.findall(r'\)', sentence)
            double_quote_count = double_quote_count + len(left_double_quotes) - len(right_double_quotes)
            single_quote_count = single_quote_count + len(left_single_quotes) - len(right_single_quotes)
            book_title_count = book_title_count + len(left_book_title) - len(right_book_title)
            parenthesis_count = parenthesis_count + len(left_parenthesis) - len(right_parenthesis)
            if double_quote_count == 0 and single_quote_count == 0 and book_title_count == 0 and parenthesis_count == 0:
                sentences.append(''.join(paragraph_sentences))
                paragraph_sentences = []
    return sentences


def counting(data: List[Dict[str, str]], counting_type: str = "char"):

    def tokenize(text: str):
        tokens = posseg.lcut(text, HMM=False)
        tokens = [(token.word, token.flag) for token in tokens]
        tokens = [token if not re.match(r"\d+(\.\d+)?", token[0]) else ('0', "m") for token in tokens]
        return tokens

    results = Counter()
    if counting_type == "char":
        for item in tqdm(data, desc="char counting"):
            chars = list(item["sentence"])
            chars = [char if not re.match(r"\d", char) else '0' for char in chars]
            results.update(chars)
    elif counting_type == "word":
        for item in tqdm(data, desc="word counting"):
            words = tokenize(item["sentence"])
            words = [word[0] for word in words]
            results.update(words)
    elif counting_type == "pos_tag":
        for item in tqdm(data, desc="pos tag counting"):
            pos_tags = tokenize(item["sentence"])
            pos_tags = [pos_tag[1] for pos_tag in pos_tags]
            results.update(pos_tags)
    return results


def main():
    src_dir = "/mnt/DATA/essay_corpus/categorized"
    total_data = {}
    for root_dir, folders, file_names in os.walk(src_dir):
        total_data[root_dir] = []
        for file_name in file_names:
            file_path = os.path.join(root_dir, file_name)
            with open(file_path, 'r', encoding="utf-8") as rf:
                for line in rf.readlines():
                    total_data[root_dir].append(json.loads(line.strip()))
    result_sentences = []
    for key, value in total_data.items():
        if len(value) > 0:
            split_path = key.split('/')
            grade = split_path[-1] if split_path[-1] != "misc" else split_path[-2]
            for item in tqdm(value, desc="working on %s..." % key):
                result_sentences.extend(cut_sentence(item, grade))
    print("There are %d sentences to be examined..." % len(result_sentences))
    dest_file = "/mnt/DATA/essay_corpus/sentences/Jul_23.jsonline"
    with open(dest_file, 'w', encoding="utf-8") as wf:
        for item in result_sentences:
            wf.write(json.dumps(item, ensure_ascii=False))
            wf.write('\n')


def check_with_id(file_id: str):
    file_path = "/mnt/DATA/essay_corpus/raw_data/filtered_Jul_17.jsonline"
    with open(file_path, 'r', encoding="utf-8") as rf:
        for line in rf.readlines():
            temp_dict = json.loads(line.strip())
            if temp_dict["id"] == file_id:
                print(temp_dict)
                break


def word_count_statistic():
    file_path = "char_count.txt"
    stat_data = []
    total_count = 0
    max_word_len = 0
    longest_word = None
    with open(file_path, 'r', encoding="utf-8") as rf:
        for line in rf.readlines():
            parts = line.strip().split(',')
            if len(parts) != 2:
                continue
            stat_data.append((parts[0], int(parts[1])))
            total_count += int(parts[1])
            if len(parts[0]) > max_word_len:
                max_word_len = len(parts[0])
                longest_word = parts[0]
    threshold = int(total_count * 0.95)
    total_count = 0
    for i, item in enumerate(stat_data):
        total_count += item[1]
        if total_count > threshold:
            break
    return i, item, max_word_len, longest_word


def split_data_set(file_path: str, target_dir: str, file_size: int = 1000000, target_file_prefix: str = "batch_"):
    temp_list = []
    with open(file_path, 'r', encoding="utf-8") as rf:
        for line in rf.readlines():
            temp_list.append(json.loads(line.strip()))
    batch_num = 0
    while (batch_num + 1) * file_size < len(temp_list):
        result_list = temp_list[batch_num * file_size: (batch_num + 1) * file_size]
        file_name = os.path.join(target_dir, target_file_prefix + "%d" % batch_num)
        with open(file_name, 'w', encoding="utf-8") as wf:
            for item in tqdm(result_list, desc="working on %s" % file_name):
                wf.write(json.dumps(item, ensure_ascii=False))
                wf.write('\n')
        batch_num += 1


if __name__ == '__main__':
    # src_file_path = "/mnt/DATA/essay_corpus/sentences/Jul_23.jsonline"
    # temp_data = []
    # with open(src_file_path, 'r', encoding="utf-8") as rf:
    #     for line in rf.readlines():
    #         temp_data.append(json.loads(line.strip()))
    # final_results = counting(temp_data, "char")
    # pairs = final_results.most_common()
    # with open("char_count.txt", 'w', encoding="utf-8") as wf:
    #     for pair in pairs:
    #         wf.write(pair[0] + ',' + str(pair[1]))
    #         wf.write('\n')
    split_data_set("/mnt/DATA/essay_corpus/sentences/Jul_23.jsonline", "/mnt/DATA/essay_corpus/word_vector_training")
