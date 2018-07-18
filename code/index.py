# -*- coding: utf-8 -*-
import configparser
import jieba
import sys
from os import listdir
import xml.etree.ElementTree as ET
import jieba
import sys
import sqlite3


class Doc:
    docid = 0
    date_time = ''
    tf = 0
    ld = 0

    def __init__(self, docid, date_time, tf, ld):
        self.docid = docid
        self.date_time = date_time
        self.tf = tf
        self.ld = ld

    def __repr__(self):
        return (str(self.docid) + "\t" + self.date_time + str(self.tf) + "\t" + str(self.ld))

    def __str__(self):
        return (str(self.docid) + "\t" + self.date_time + str(self.tf) + "\t" + str(self.ld))


class IndexModule:
    postings_lists = {}
    stop_words = set()

    config_path = ''
    config_encoding = ''

    def __init__(self, config_path, config_encoding):
        self.config_path = config_path
        self.config_encoding = config_encoding
        config = configparser.ConfigParser()
        config.read(config_path, config_encoding)
        # 读取停用词
        ff = open(config['DEFAULT']['stop_words_path'], encoding='utf-8')
        words = ff.read()
        self.stop_words = set(words.split('\n'))

    def is__number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    # 过滤停用词
    def clean_list(self, seg_list):
        cleaned_dict = {}
        n = 0
        for i in seg_list:
            i = i.strip().lower()
            if i != '' and not self.is__number(i) and i not in self.stop_words:
                n = n + 1
                if i in cleaned_dict:
                    cleaned_dict[i] = cleaned_dict[i] + 1
                else:
                    cleaned_dict[i] = 1
            return n, cleaned_dict

            # 文档写入数据库
    def write_postings_to_db(self, db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute('''DROP TABLE IF EXISTS postings''')
        c.execute('''CREATE TABLE postings
                     (term TEXT PRIMARY KEY, df INTEGER, docs TEXT)''')

        for key, value in self.postings_lists.items():
            doc_list = '\n'.join(map(str, value[1]))
            t = (key, value[0], doc_list)
            c.execute("INSERT INTO postings VALUES (?, ?, ?)", t)

        conn.commit()
        conn.close()


    # 文档构建索引
    def construct_postings_lists(self):
        config = configparser.ConfigParser()
        config.read(self.config_path, self.config_encoding)
        files = listdir(config['DEFAULT']['doc_dir_path'])
        AVG_L = 0
        for i in files:
            root = ET.parse(config['DEFAULT']['doc_dir_path'] + i).getroot()
            title = root.find('title').text
            body = root.find('body').text
            docid = int(root.find('id').text)
            date_time = root.find('datetime').text
            seg_list = jieba.lcut(title + '。' + body, cut_all=False)

            # ld 文档长度
            ld, cleaned_dict = self.clean_list(seg_list)

            AVG_L = AVG_L + ld

            for key, value in cleaned_dict.items():
                d = Doc(docid, date_time, value, ld)
                if key in self.postings_lists:
                    # df 文档频率
                    self.postings_lists[key][0] = self.postings_lists[key][0] + 1  # df++
                    self.postings_lists[key][1].append(d)
                else:
                    self.postings_lists[key] = [1, [d]]  # [df, [Doc]]

        AVG_L = AVG_L / len(files)
        config.set('DEFAULT', 'N', str(len(files)))
        config.set('DEFAULT', 'avg_l', str(AVG_L))
        with open(self.config_path, 'w') as configfile:
            config.write(configfile)
        self.write_postings_to_db(config['DEFAULT']['db_path'])


if __name__ == "__main__":
    seg_list = jieba.cut("我毕业于清华大学")
    print("Default Mode:" + "-".join(seg_list))

    im = IndexModule('E:/github/myengine/config.ini', 'utf-8')
    im.construct_postings_lists()
