# from transformers import  pipeline
# from transformers import BertTokenizer, BertForTokenClassification
#
# # tokenizer
# model_name = 'bert-base-chinese'
# model_name = 'hfl/chinese-bert-wwm-ext'
# model =  BertForTokenClassification.from_pretrained(model_name)
# tokenizer = BertTokenizer.from_pretrained(model_name)
# ner_recognizer = pipeline('ner', model=model, tokenizer=tokenizer)
#
# text = '中国的首都是北京。'
# text1 = 'This model can be loaded on the Inference API on-demand.'
# for item in ner_recognizer(text):
#     print(item)
#
# nlp = pipeline('ner')
# sequence = "Hugging Face Inc. is a company based in New York City. Its headquarters are in DUMBO, therefore very close to the Manhattan Bridge which is visible from the window."
# for item in nlp(sequence):
#     print(item)
import os
from ltp import LTP
import logging
from config import LTP4_MODEL_DIR
from config import ENTMT_ES_INDEX
from config import USER_DICT_DIR
from config import MONGODB_HOST, MONGODB_PORT, MONGODB_DATABASE_NAME, MONGODB_ENTMT_COLLECTION
from pymongo import MongoClient
from multiprocessing import Pool, Process
from EventExploreServer.component import search_all_do
from django.test import TestCase
from ltp.utils import split_sentence

# ltp = LTP(path=LTP4_MODEL_DIR)
debug_logger = logging.getLogger('debug')
# ltp0 = LTP(LTP4_MODEL_DIR)
# ltp1 = LTP(LTP4_MODEL_DIR)
# ltp2 = LTP(LTP4_MODEL_DIR)
# ltp3 = LTP(LTP4_MODEL_DIR)
# ltp4 = LTP(LTP4_MODEL_DIR)
# ltp5 = LTP(LTP4_MODEL_DIR)
# ltp6 = LTP(LTP4_MODEL_DIR)
# # ltp7 = LTP(LTP4_MODEL_DIR)
# # ltp8 = LTP(LTP4_MODEL_DIR)
# # ltp9 = LTP(LTP4_MODEL_DIR)
# # ltps = [ltp0, ltp1, ltp2, ltp3, ltp4, ltp5, ltp6, ltp7, ltp8, ltp9]
# ltps = [ltp0, ltp1, ltp2, ltp3, ltp4, ltp5, ltp6 ]


def mongo2ner(idx, ltp, offset, size):
    """
    根据offset从mongo中取指定size的文章
    :param idx:
    :param offset:
    :param size:
    :return:
    """
    entities = []
    pid = os.getpid()
    try:
        # debug_logger.debug("{} ---pid:{} MongoDB: Skip: {}, size: {}".format(idx, pid, offset, size))
        ltp = LTP(path=LTP4_MODEL_DIR)
        db_connect = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
        db = db_connect[MONGODB_DATABASE_NAME]
        coll = db[MONGODB_ENTMT_COLLECTION]
        # debug_logger.debug("pid: {}, connected".format(pid))
        for art in coll.find(skip=offset, limit=size):
            debug_logger.debug(art['title'])
            text = art['title'] + art['content']
            entities_of_art = get_article_entities(idx, text, ltp)
            entities += entities_of_art

        # debug_logger.debug("pid: {}, write".format(pid))
        with open(os.path.join(USER_DICT_DIR, 'ners_' + str(idx) + '.txt'), 'w') as fw:
            for item in entities:
                for word, label in item:
                    fw.write(word + '\t' + label + '\n')
    except Exception as e:
        print("ERROR mongo2ner: {}".format(e))
        # debug_logger.debug("ERROR mongo2ner: {}".format(e))
    return entities


def get_article_entities(idx, text, ltp):
    """
    对每篇文章提取命名实体
    :param article:
    :param ltp:
    :return:
    """
    entities = []
    try:
        sents = split_sentence(text)
        seg, hidden = ltp.seg(sents)
        nertags = ltp.ner(hidden)
        # seg, hidden = ltps[idx%7].seg(sents)
        # nertags = ltps[idx%7].ner(hidden)
        # 用dict
        for idx1, tags_of_sent in enumerate(nertags):
            for tag in tags_of_sent:
                # print(tag)
                label, start, end = tag
                word = "".join(seg[idx1][start:end+1])
                if len(word) < 2:
                    continue
                # print(word)
                entities.append((word, label))
                # if word not in entities:
                #     entities[word] = t
        # print(entities)
    except Exception as e:
        print("ERROR get_article_entites: {}".format(e))
        # debug_logger.debug("ERROR get_article_entites: {}".format(e))
    return entities



class TestExtractNER(TestCase):

    def test_extract_all_ners(self):
        """
        Deprecation
        :return:
        """
        debug_logger.setLevel(logging.DEBUG)
        entities = search_all_do(ENTMT_ES_INDEX, size=None, func=get_article_entities, func_return_type='dict')
        # for entity, tag in entities.items():
        #     print(entity, tag)

        import os
        with open(os.path.join(USER_DICT_DIR, 'extract_ners.txt'), 'w') as fw:
            for entity, tag in entities.items():
                fw.write(entity+'\t'+tag+'\n')
        print(len(entities.keys()))


    def test_extract_all_ners_multi_process(self):
        import os
        from math import ceil
        debug_logger.setLevel(logging.DEBUG)
        db_connect = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
        db = db_connect[MONGODB_DATABASE_NAME]
        coll = db[MONGODB_ENTMT_COLLECTION]
        # p = Pool(10)
        size = 10000
        size = 20
        art_count = coll.count_documents({})
        entity_dict = {}

        p1 = Process(target=mongo2ner, args=(1,  1, 0, size))
        p1.start()
        p1.join()

        # rets = []
        # for i in range(ceil(art_count/size)):
        #     print(i)
        #     if i>5: break
        #     offset = i*size
        #     ret = p.apply_async(func=mongo2ner, args=(i, ltps[i%10], offset, size, ))
        #     rets.append(ret)
        # p.close()
        # p.join()
        #
        # for ret in rets:
        #     print(ret.get())
        #     for item in ret.get():
        #         for word, label in item:
        #             if word not in entity_dict.keys():
        #                 entity_dict[word] = label
        #
        # with open(os.path.join(USER_DICT_DIR, 'extract_ners.txt'), 'w') as fw:
        #     for word, label in entities.items():
        #         fw.write(word+'\t'+label+'\n')


    def test_nlp_model(self):
        ltp1 = LTP(LTP4_MODEL_DIR)
        ltp2 = LTP(LTP4_MODEL_DIR)
        ltp3 = LTP(LTP4_MODEL_DIR)
        ltp4 = LTP(LTP4_MODEL_DIR)
        ltp5 = LTP(LTP4_MODEL_DIR)
        ltp6 = LTP(LTP4_MODEL_DIR)
        ltp7 = LTP(LTP4_MODEL_DIR)
        print('-------')
        import time
        time.sleep(10)

if __name__ == '__main__':
    debug_logger.setLevel(logging.DEBUG)
    entities = search_all_do(ENTMT_ES_INDEX, size=None, func=get_article_entities, func_return_type='dict')
    # for entity, tag in entities.items():
    #     print(entity, tag)

    import os

    with open(os.path.join(USER_DICT_DIR, 'extract_ners.txt'), 'w') as fw:
        for entity, tag in entities.items():
            fw.write(entity + '\t' + tag + '\n')
    print(len(entities.keys()))
