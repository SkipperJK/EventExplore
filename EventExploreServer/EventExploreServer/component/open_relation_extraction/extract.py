import logging
from django.test import TestCase
# from EventExploreServer.utils.utils import split_sentence
from ltp.utils import split_sentence
from EventExploreServer.component.nlp_annotator.nlp import nlp
from EventExploreServer.component.open_relation_extraction.extractor import Extractor

# nlp = NLP()
extractor = Extractor()
debug_logger = logging.getLogger('debug')
root_logger = logging.getLogger('root')
trace_logger = logging.getLogger('trace')


def extract_text(text, generalization=True):
    """
    对输入对文本进行关系抽取
    :param text:
    :return: Triple元素的二维list
    """
    origin_sentences = split_sentence(text)
    debug_logger.debug("{}".format("\n".join(origin_sentences)))
    lemmas, hidden = nlp.segment(origin_sentences)
    words = nlp.postag(lemmas, hidden)
    words = nlp.nertag(words, hidden)  # add NER tag
    sentences = nlp.dependency(words, hidden)

    triples = []
    for idx_sent, sent in enumerate(origin_sentences):
        triples_of_sent = extractor.extract(sent, sentences[idx_sent], idx_sent)
        triples.append(triples_of_sent)
    return triples



def extract_article(article, idx_document=0, generalization=False):
    """
    对一个ArticleES中的title和content进行关系元组抽取
    :param article: ArticleES对象
    :param generalization: 对抽取的元组泛化处理
    :return: Triple元素的二维list
    """

    origin_sentences = article.sentence_of_title + article.sentence_of_content
    lemmas, hidden = nlp.segment(origin_sentences)
    words_postag = nlp.postag(lemmas, hidden)
    words_nertag = nlp.nertag(words_postag, hidden)
    sentences = nlp.dependency(words_nertag, hidden)

    triples = []
    for idx_sent, sent in enumerate(origin_sentences):
        trace_logger.info("Sentence {}: {}".format(idx_sent+1, sent))
        # debug_logger.debug(sent)
        # for word in sentences[idx_sent].words:
        #     debug_logger.debug(word.to_string())
        triples_of_sent = extractor.extract(sent, sentences[idx_sent], idx_sent, idx_document)
        triples.append(triples_of_sent)
    for ts_of_sent in triples:
        for t in ts_of_sent:
            # debug_logger.debug(t.to_string())
            trace_logger.info(t.to_string())

    if not generalization:
        return triples

    trace_logger.info('Generalizing triples...')
    generalization_triples = []
    for triples_of_sent in triples:
        tmp = []
        for triple in triples_of_sent:
            tmp.extend(triple.gts)
        generalization_triples.append(tmp)
    return generalization_triples



class TestExtract(TestCase):
    """
    继承unittest.TestCase，类的成员变量以test的开头的被认为是测试方法，测试时会执行
    """

    def test_extract_text(self):
        # DSNF2：正常，coo verb, sub coo
        text1 = '''
        习近平主席访问奥巴马总统。
       习近平主席访问奥巴马总统先生。习近平主席同志访问奥巴马总统先生。
       习近平主席视察厦门，李克强访问香港。
       习近平来我家了，我跑着去迎接。
       习近平视察并访问厦门。
       拉里佩奇和谢尔盖布林创建Google。
       马云创建了阿里巴巴、蚂蚁金服和淘宝。
       习近平主席同志和奥巴马总统先生一同访问非洲。
       张三访问非洲和慰问小明。
       张三访问和慰问小明。
       张三视察和访问巴西。
       张三访问并慰问小明。
       张三视察并访问小明。
       张三视察并访问巴西。
       张三视察并访问Google。
                张三，李四和小明都去了美国。
                小明去了美国，英国和法国。
        '''

        # DSNF1
        text2 = '''
        中国的主席习近平。
        美国的奥巴马总统。
        美国前任总统奥巴马访问中国。
        华盛顿警方发现证据。
        '''

        # DSNF2 + DSNF3
        text3 = "中国国家主席习近平访问韩国，并在首尔大学发表演讲"

        # 不及物动词 DSNF4, DSNF4+sub coo
        text5 = '''
        小明毕业于哈佛大学。
        小明和小红毕业于哈佛大学。
        小明毕业于哈佛大学和剑桥大学。
        小明和小红毕业于哈佛大学和剑桥大学。
        '''

        # DSNF3 1.不及物动词 2.及物动词后无宾语，用介词短语修饰
        text6 = '''习近平主席对埃及进行国事访问。
                习近平在上海视察。
                习近平在上海视察并讲话。
                习近平和李克强对埃及进行国事访问。
                习近平在上海和杭州视察。
                小明到达非洲并对埃及进行访问。
                小明被小红打了。
                '''
        debug_logger.setLevel(logging.DEBUG)
        triples = []
        triples += extract_text(text2)
        triples += extract_text(text1)
        triples += extract_text(text6)
        triples += extract_text(text5)
        triples += extract_text("厦门大学的朱崇实校长. 中国北京的小明先生。")
        for triple_of_sent in triples:
            for triple in triple_of_sent:
                print(triple.to_string())
                attrs, relation = triple.convert2knowledge()
                print('attrs: {}'.format(attrs))
                print('relation: {}'.format(relation))

    def test_check_and_fix(self):
        text = '''
        杨紫琼接班人张三
        
        '''
        text = "但是造化弄人，李小龙在年仅30多岁就意外死亡，但中国功夫电影没有停止发展，不断涌现出李连杰、成龙、甄子丹等优秀的功夫明星。"
        # debug_logger.setLevel(logging.DEBUG)
        triples = extract_text(text)

        for triples_of_sent in triples:
            for triple in triples_of_sent:
                root_logger.info(triple.to_string())


    def test_split_sentence(self):
        text1 = '''
                习近平主席访问奥巴马总统。
               习近平主席访问奥巴马总统先生。习近平主席同志访问奥巴马总统先生。
               习近平主席视察厦门，李克强访问香港。
               习近平来我家了，我跑着去迎接。
               习近平视察并访问厦门。
               拉里佩奇和谢尔盖布林创建Google。
               马云创建了阿里巴巴、蚂蚁金服和淘宝。
               习近平主席同志和奥巴马总统先生一同访问非洲。
               张三访问非洲和慰问小明。
               张三访问和慰问小明。
               张三视察和访问巴西。
               张三访问并慰问小明。
               张三视察并访问小明。
               张三视察并访问巴西。
               张三视察并访问Google。
                        张三，李四和小明都去了美国。
                        小明去了美国，英国和法国。
                '''
        from ltp.utils import split_sentence
        for sent in split_sentence(text1):
            print(sent)