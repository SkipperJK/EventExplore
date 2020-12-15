import os
import logging
from ltp import LTP
from config import LTP4_MODEL_DIR, USER_DICT_DIR
from EventExploreServer.model.Word import WordUnit
from EventExploreServer.model.Sentence import SentenceUnit

trace_logger = logging.getLogger('trace')


class NLP:
    """
    在LTP分析的结果上进行封装

    """

    def __init__(self, default_model_dir = LTP4_MODEL_DIR, user_dict_dir = USER_DICT_DIR):
        self.ltp = LTP(path=default_model_dir)
        for file in os.listdir(user_dict_dir):
            self.ltp.init_dict(path=os.path.join(user_dict_dir, file))

    def segment(self, sentences):
        lemmas, hidden = self.ltp.seg(sentences)
        return lemmas, hidden

    def postag(self, lemmas, hidden):
        """
        根据postag的结果抽取words
        :param lemmas:
        :param hidden:
        :return:
        """
        words = []
        postags = self.ltp.pos(hidden)
        for idx_sent, postags_sent in enumerate(postags):
            words_sent = []
            for i in range(len(postags_sent)):
                # 词的编号从1开始
                word = WordUnit(i+1, lemmas[idx_sent][i], postags_sent[i])
                words_sent.append(word)
            words.append(words_sent)
        # for i in range(len(postags)):
        #     word = WordUnit(i+1, lemmas[i], postags[i])
        #     words.append(word)
        return words

    def nertag(self, words, hidden):
        """
        根据nertag的结果抽取words，将ner得到的信息作为pos的纠正和补充，例如n->ni/ns/nl
        :param lemmas:
        :param hidden:
        :return:
        """
        # Nh 人名     Ni 机构名      Ns 地名
        nertags = self.ltp.ner(hidden)
        '''
        为了进行三元组提取，使用到ner信息，需要将一些ner分析后的词进行合并得到新词。
        NOTE：NER之后可能将一些tokens合并成一个word
        例如：
            [['高克', '访问', '中国', '，', '并', '在', '同济', '大学', '发表', '演讲', '。']]
            [['nh', 'v', 'ns', 'wp', 'c', 'p', 'nz', 'n', 'v', 'v', 'wp']]
            [[('Nh', 0, 0), ('Ns', 2, 2), ('Ni', 6, 7)]]
            [[(1, 2, 'SBV'), (2, 0, 'HED'), (3, 2, 'VOB'), (4, 2, 'WP'), (5, 9, 'ADV'), (6, 9, 'ADV'), (7, 8, 'ATT'), (8, 6, 'POB'), (9, 2, 'COO'), (10, 9, 'VOB'), (11, 2, 'WP')]]
        '''
        ner2pos = {'Nh':'nh', 'Ns':'ns', 'Ni':'ni'}
        n = 1
        #for i in range(len(words)):
        for idx_sent, nertags_sent in enumerate(nertags):
            for item in nertags_sent:
                for i in range(item[1], item[2]+1):
                    words[idx_sent][i].nertag = item[0]
                    words[idx_sent][i].postag = ner2pos[item[0]]
        # for item in nertags:
        #     for i in range(item[1], item[2]+1):
        #         words[i].postag = ner2pos[item[0]]
        return words

    def dependency(self, words, hidden):
        """
        根据dp结果，抽取words信息，用于之后的三元组抽取。（主要是词之间的依赖关系）
        :param hidden:
        :return:
        """
        sentences = []
        dep = self.ltp.dep(hidden)
        for idx_sent, dep_sent in enumerate(dep):
            for i in range(len(words[idx_sent])):
                if i < len(dep_sent):  # [(1, 2, 'ATT'), (2, 3, 'ATT')]] 省略了(3, 0, 'HED)
                    words[idx_sent][i].head = dep_sent[i][1]
                    words[idx_sent][i].dependency = dep_sent[i][2]
            sentences.append(SentenceUnit(words[idx_sent]))
        return sentences


if __name__ == '__main__':
    sent = ["高克访问中国，并在同济大学发表演讲。"]
    nlp = NLP()
    lemmas, hidden = nlp.segment(sent)
    print(lemmas)
    words_postag = nlp.postag(lemmas, hidden)
    words_nertag = nlp.nertag(words_postag, hidden)
    sentences = nlp.dependency(words_nertag, hidden)
    for sent in sentences:
        for word in sent.words:
            print(word.__dict__)
