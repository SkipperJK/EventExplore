import logging
from django.test import TestCase
from EventExploreServer.component.open_relation_extraction.nlp import NLP
from EventExploreServer.component.open_relation_extraction.extractor import Extractor

nlp = NLP()
extractor = Extractor()
debug_logger = logging.getLogger('debug')
root_logger = logging.getLogger('root')
trace_logger = logging.getLogger('trace')
if 'DEBUG' not in locals().keys():
    DEBUG = True if debug_logger.level == logging.DEBUG else False


def extract(origin_sentences, idx_document=0, generalization=False):
    """
    对一个document中的多个句子进行关系元组抽取
    :param origin_sentences: list
    :param idx_document: int
    :return: Triple的二维list
    """
    trace_logger.info('Starting extract triples ...')
    lemmas, hidden = nlp.segment(origin_sentences)
    words_postag = nlp.postag(lemmas, hidden)
    words_nertag = nlp.nertag(words_postag, hidden)
    sentences = nlp.dependency(words_nertag, hidden)

    triples = []
    for idx_sent, sent in enumerate(origin_sentences):
        if DEBUG:
            debug_logger.debug(sent)
            for word in sentences[idx_sent].words:
                debug_logger.debug(word.to_string())
        triples_of_sent = extractor.extract(sent, sentences[idx_sent], idx_sent, idx_document)
        triples.append(triples_of_sent)
    if DEBUG:
        for ts_of_sent in triples:
            for t in ts_of_sent:
                debug_logger.debug(t.to_string())

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

    def test_extract(self):
        origin_sentences = [
            "习近平主席访问奥巴马总统先生",
            "习近平主席视察厦门，李克强访问香港",
            "李克强总理今天来我家了，我赶紧往家里跑。",
            "浮士德与魔鬼达成协议。",
            "巴拿马在2007年与中国建立关系。",
            "德国总统高克。",
            "高克访问中国。",
            "习近平在上海视察。",
            "习近平对埃及进行国事访问。",
            "奥巴马毕业于哈佛大学。",
            "习近平主席和李克强总理接见普京。",
            "习近平访问了美国和英国。",
            "高克访问中国，并在同济大学发表演讲。",
            "李明出生于1999年。"
        ]

        triples = extract(origin_sentences, generalization=True)
        for triples_of_sent in triples:
            for triple in triples_of_sent:
                root_logger.info(triple.to_string())
