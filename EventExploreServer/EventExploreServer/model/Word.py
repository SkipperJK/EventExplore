from django.test import TestCase


class WordUnit:
    """词单元组成
    postag标签
        'n'<--->general noun 普通名词        'i'<--->idiom 成语                       'j'<--->abbreviation 缩写词
        'ni'<--->organization name 机构名称   'nh'<--->person name 人名                'nl'<--->location noun 位置名词
        'ns'<--->geographical name 地名      'nz'<--->other proper noun 其他专有名词    'ws'<--->foreign words
    nertag标签
        'Nh' 人名
        'Ni' 机构名
        'Ns' 地名
    """
    # 定义类变量
    # 当前词在句子中的序号，1开始
    ID = 0
    # 当前词语的原型(或标点)，就是切分后的一个词
    lemma = ''
    # 当前词语的词性
    postag = ''
    # 当前词语的中心词，及当前词的头部词
    head = 0  # 指向词的ID
    head_word = None # 该中心词单元
    # 当前词语与中心词的依存关系
    dependency = '' # 每个词都有指向自己的唯一依存

    def __init__(self, ID, lemma, postag, nertag='', head=0, head_word=None, dependency='', hidden=None):
        self.ID = ID
        self.lemma = lemma
        self.postag = postag
        self.nertag = nertag
        self.head = head
        self.head_word = head_word
        self.dependency = dependency
        self.hidden = hidden

    def get_id(self):
        return self.ID
    def set_id(self, ID):
        self.ID = ID

    def get_lemma(self):
        return self.lemma
    def set_lemma(self, lemma):
        self.lemma = lemma

    def get_postag(self):
        return self.postag
    def set_postag(self, postag):
        self.postag = postag

    def get_nertag(self):
        return self.nertag
    def set_nertag(self, nertag):
        self.nertag = nertag

    def get_head(self):
        return self.head
    def set_head(self, head):
        self.head = head

    def get_head_word(self):
        return self.head_word
    def set_head_word(self, head_word):
        self.head_word = head_word

    def get_dependency(self):
        return self.dependency
    def set_dependency(self, dependency):
        self.dependency = dependency

    def to_string(self):
        """将word的相关处理结果转成字符串，tab键间隔
        Returns:
            word_str: str，转换后的字符串
        """
        return "ID: {0:>2d}, lemma: {1:{7}>5s}, postag: {2:>3s}, " \
               "nertag: {3:>3s}, head: {4:>5d}, head_word: {5:{7}>5s}, dependency: {6:>5s}".format(
            self.ID,
            self.lemma,
            self.postag,
            self.nertag,
            self.head,
            str(self.head_word),
            self.dependency,
            chr(12288)
        )

    def __str__(self):
        return self.lemma



class TestWord(TestCase):

    def testWord(self):
        # 中国首都北京
        word3 = WordUnit(3, '北京', 'ns', nertag='Ns',  head=0, head_word=None, dependency='HED')
        word2 = WordUnit(2, '首都', 'ns', nertag='', head=3, head_word=word3, dependency='ATT')
        word1 = WordUnit(1, '中国', 'ns', nertag='Ns', head=2, head_word=word2, dependency='ATT')

        print(word1.lemma + '\t' + word1.postag)
        print(word2.lemma + '\t' + word2.head_word.lemma)
        print(word3.get_lemma() + '\t' + word3.get_postag())

        print(word1.to_string())
        print(word2.to_string())
        print(word3.to_string())

