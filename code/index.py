import configparser
import jieba
import sys
from os import listdir
import xml.etree.ElementTree as ET
import jieba
import sys
import sqlite3
sys.setdefaultencoding("utf-8")

class Doc:
    docid = 0
    date_time = ''
    tf = 0
    ld = 0

    def __init__(self,docid,date_time,tf,ld):
        self.docid = docid
        self.date_time = date_time
        self.tf = tf
        self.ld = ld

    def __repr__(self):
        return (str(self.docid)+"\t"+self.date_time+str(self.tf)+"\t"+str(self.ld))

    def __str__(self):
        return (str(self.docid)+"\t"+self.date_time+str(self.tf)+"\t"+str(self.ld))


class IndexModule:
    postling_lists = {}
    stop_words = set()

    config_path = ''
    config_encoding = ''

    def __init__(self,config_path,config_encoding):
        self.config_path = config_path
        self.config_encoding = config_encoding
        config = configparser.CongigParser()
        config.read(config_path,config_encoding)
        #读取停用词
        ff = open(config['DEFAULT']['stop_words_path'])
        words = ff.read()
        self.stop_words = set(words.split('\n'))

    def is__number(self,s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    #过滤停用词
    def clean_list(self,seg_list):
        cleaned_dict = {}
        n=0
        for i in seg_list:
            i=i.strip().lower()
            if i !='' and not self.is__number(i)and i not in self.stop_words:
                n = n+1
                if i in cleaned_dict:
                    cleaned_dict[i]=cleaned_dict[i]+1
                else:
                    cleaned_dict[i] = 1
            return n,cleaned_dict

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


if __name__ == "__main__":
    seg_list = jieba.cut("我毕业于清华大学")
    print("Default Mode:" + "-".join(seg_list))

    im = IndexModule('../config.ini', 'utf-8')
    im.construct_postings_lists()



