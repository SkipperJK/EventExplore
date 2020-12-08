import logging
from django.test import TestCase
from EventExploreServer.component import search_articles, extract_article
from EventExploreServer.component import WordGraph
from EventExploreServer.component.word_link.TripleNetwork import TripleNetwork


debug_logger = logging.getLogger('debug')
trace_logger = logging.getLogger('trace')
root_logger = logging.getLogger('root')
debug_logger.setLevel(logging.INFO)

word_graph = WordGraph()
triple_net = TripleNetwork()



def explore(articles):
    """
    进行OpenIE并进行分析 --- TODO; 这个不应该叫explore，explore应该是整个系统流程合并，输入是topic
    :param articles:
    :return:
    """
    triples = []
    for idx, art in enumerate(articles):
       for triple_of_sent in extract_article(art, idx):
           for triple in triple_of_sent:
               triples.append(triple)
    data = triple_net(triples, articles)
    return data







class TESTMAIN(TestCase):

    def test_event_explore(self):
        topic = "马航MH370"

        ids_article = []
        articles = search_articles(topic, 2)
        triples = []
        for idx, art in enumerate(articles):
            ids_article.append(art.id)
            trace_logger.info("idx: {}, title: {}".format(idx, art.title))
            # sentences = art.sentence_of_title + art.sentence_of_content
            for triple_of_sent in extract_article(art, idx):
                for triple in triple_of_sent:
                    triple.docID = art.id
                    triples.append(triple)
            # tmp = extract(sentences, idx)
            # triples.append(tmp)
        for triple in triples:
            trace_logger.info(str(triple))
        # word_graph(triples, articles)
        # for word in word_graph.dictionary:
        #     trace_logger.info(word)
        # trace_logger.info(word_graph.adjacency_mat)
        # trace_logger.info(word_graph.word_related_articles)


        data = triple_net(triples, articles)
        for word in triple_net.dictionary:
            trace_logger.info(word)
        trace_logger.info(triple_net.adjacency_mat)
        trace_logger.info(triple_net.edge_word_mat)
        import json
        print(json.dumps(data, indent=4, ensure_ascii=False))

        # triples = []
        # topic = "奥斯卡提名"
        # # topic = "艾塞罗比亚"
        # topic = "埃塞俄比亚"
        # articles = search_articles(topic, 40)
        # for idx, art in enumerate(articles):
        #     if art.id in ids_article: continue
        #     trace_logger.info("idx: {}, title: {}".format(idx, art.title))
        #     sentences = art.sentence_of_title + art.sentence_of_content
        #     for triple_of_sent in extract_article(art, idx):
        #         for triple in triple_of_sent:
        #             triple.docID = art.id
        #             triples.append(triple)
        #
        # word_graph(triples, articles)
        #
        #
        # for word in word_graph.dictionary:
        #     trace_logger.info(word)
        # trace_logger.info(word_graph.adjacency_mat)
        # trace_logger.info(word_graph.word_related_articles)
