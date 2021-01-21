from pymongo import MongoClient
from ltp import LTP
from ltp.utils import split_sentence
import os
import sys
import logging
import time

LTP4_MODEL_DIR = "../../../data/pretrained_model/LTPModel/"
MONGODB_HOST = "10.176.24.41"
MONGODB_PORT = 27017
MONGODB_DATABASE_NAME = "Sina"
MONGODB_ARTICLE_COLLECTION = "article20191121_sim"
MONGODB_ENTMT_COLLECTION = "article20190413_sim"
BULK_SIZE = 2000
ENTITY_DIR = "../../../data/entity/"


if __name__ == '__main__':

    idx = int(sys.argv[1])
    offset = int(sys.argv[2])
    size = int(sys.argv[3])
    entities = []
    pid = os.getpid()
    batch_size = 10 # 避免timeout
    try:
        start = time.time()
        print("{} ---pid:{} MongoDB: Skip: {}, size: {}".format(idx, pid, offset, size))
        # # debug_logger.debug("{} ---pid:{} MongoDB: Skip: {}, size: {}".format(idx, pid, offset, size))
        ltp = LTP(path=LTP4_MODEL_DIR)
        db_connect = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
        db = db_connect[MONGODB_DATABASE_NAME]
        coll = db[MONGODB_ENTMT_COLLECTION]
        i = 0
        for art in coll.find(skip=offset, limit=size, no_cursor_timeout=True).batch_size(batch_size):
            print('pid: {}, {}, title: {}'.format(pid, i, art['title']))
            text = art['title'] + art['content']
            sents = split_sentence(text)
            seg, hidden = ltp.seg(sents)
            nertags = ltp.ner(hidden)
            for idx1, tags_of_sent in enumerate(nertags):
                for tag in tags_of_sent:
                    label, start, end = tag
                    word = "".join(seg[idx1][start:end + 1])
                    if len(word) < 2:
                        continue
                    entities.append((word, label))
            i += 1
        print(entities)

        with open(os.path.join(ENTITY_DIR, 'ners_' + str(idx) + '.txt'), 'w') as fw:
            for item in entities:
                word, label = item
                fw.write(word + '\t' + label + '\n')
        end = time.time()
        print("Using time: {}s".format(end-start))
    except Exception as e:
        print("ERROR: {}".format(e))

