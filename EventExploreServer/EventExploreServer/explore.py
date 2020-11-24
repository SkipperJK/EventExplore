import logging
from django.test import TestCase
from EventExploreServer.component import search_articles, extract
from EventExploreServer.component import WordGraph


debug_logger = logging.getLogger('debug')
trace_logger = logging.getLogger('trace')
root_logger = logging.getLogger('root')
debug_logger.setLevel(logging.INFO)

word_graph = WordGraph()


# if __name__ == '__main__':

class TESTMAIN(TestCase):

    def test_event_explore(self):
        topic = "马航MH370"

        ids_article = []
        articles = search_articles(topic, 40)
        triples = []
        for idx, art in enumerate(articles):
            ids_article.append(art.id)
            trace_logger.info("idx: {}, title: {}".format(idx, art.title))
            sentences = art.sentence_of_title + art.sentence_of_content
            for triple_of_sent in extract(sentences, idx):
                for triple in triple_of_sent:
                    triple.docID = art.id
                    triples.append(triple)
            # tmp = extract(sentences, idx)
            # triples.append(tmp)

        word_graph(triples, articles)
        for word in word_graph.dictionary:
            trace_logger.info(word)
        trace_logger.info(word_graph.adjacency_mat)
        trace_logger.info(word_graph.word_related_articles)

        triples = []
        topic = "奥斯卡提名"
        # topic = "艾塞罗比亚"
        topic = "埃塞俄比亚"
        articles = search_articles(topic, 40)
        for idx, art in enumerate(articles):
            if art.id in ids_article: continue
            trace_logger.info("idx: {}, title: {}".format(idx, art.title))
            sentences = art.sentence_of_title + art.sentence_of_content
            for triple_of_sent in extract(sentences, idx):
                for triple in triple_of_sent:
                    triple.docID = art.id
                    triples.append(triple)

        word_graph(triples, articles)


        for word in word_graph.dictionary:
            trace_logger.info(word)
        trace_logger.info(word_graph.adjacency_mat)
        trace_logger.info(word_graph.word_related_articles)
