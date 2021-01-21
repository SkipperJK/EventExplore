import logging
from django.test import TestCase
from graphviz import Digraph
from ltp.utils import split_sentence
from EventExploreServer.component.nlp_annotator.nlp import nlp
from config import PNG_DIR


# nlp = NLP()
debug_logger = logging.getLogger('debug')


def annotate_sentence(origin_sentence):
    lemmas, hidden = nlp.segment([origin_sentence])
    words = nlp.postag(lemmas, hidden)
    words = nlp.nertag(words, hidden)  # add NER tag
    sentence = nlp.dependency(words, hidden)
    dp_graph(sentence[0])
    return sentence[0]

def annotate_text(text):

    origin_sentences = split_sentence(text)
    debug_logger.debug("{}".format("\n".join(origin_sentences)))
    lemmas, hidden = nlp.segment(origin_sentences)
    words = nlp.postag(lemmas, hidden)
    words = nlp.nertag(words, hidden)  # add NER tag
    sentences = nlp.dependency(words, hidden)
    for sent in sentences:
        dp_graph(sent)

    return sentences


def dp_graph(sentence):
    """
    绘制依存句法图
    :param sentence: SentenceUnit
    :return:
    """
    dot = Digraph(
        filename=sentence.id,
        directory=PNG_DIR,
        node_attr={
            'shape': 'record',
            'color': 'lightblue2',
            'height': '.2',
            'style': 'filled'
        },
        format='png'
    )
    for word in sentence.words:
        dot.node(str(word.ID), word.lemma)
    for word in sentence.words:
        if word.head_word:
            dot.edge(str(word.head_word.ID), str(word.ID), label=word.dependency)
    # dot.view(sentence.id)
    dot.render()


class TESTANNOTATE(TestCase):

    def test_annotate_text(self):
        import json
        from pprint import pprint
        from EventExploreServer.model.serializers import SentenceSerializer
        from EventExploreServer.model.serializers import WordSerializer
        text  = '''
        6日下午，一群特朗普的支持者冲进国会大厦，阻止了国会计票工作，当中发生了枪击事件，导致一名妇女死亡。警方疏散了议员并封锁了国会。几小时后国会大厦宣布重新开始会议。
        '''
        sentences = annotate_text(text)
        jsonSentence = SentenceSerializer(sentences, many=True).data
        # data = json.dumps(jsonSentence)
        # print(jsonSentence)
        pprint(jsonSentence)

        for sent in sentences:
            print(sent.to_string())
            print(sent.get_name_entities())

    def test_annotate_sentence(self):
        origin_sent = "奥巴马访问中国。"
        origin_sent = "6日下午，一群特朗普的支持者冲进国会大厦，阻止了国会计票工作，当中发生了枪击事件，导致一名妇女死亡。"
        sentence = annotate_sentence(origin_sent)
        print(sentence.to_string())
