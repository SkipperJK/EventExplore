import math
import logging
from py2neo import Graph, Node, Relationship
from py2neo import NodeMatcher, RelationshipMatcher
from django.test import TestCase
from EventExploreServer.utils.entity_list import all_entity_dict
from config import ENTMT_ES_INDEX
from EventExploreServer.component import search_all_do
from EventExploreServer.component import extract_article


host = '10.176.24.53'
port = 7687
user = 'neo4j'
password = 'test'

debug_logger = logging.getLogger('debug')
info_logger = logging.getLogger('info')
graph = Graph(host=host, port=port, user=user, password=password)
# print(graph.run('match (n) return n'))
# print(graph.name)


def build():
    pass


def exist(person):
    nodes = NodeMatcher(graph)
    res = nodes.match("Person", name=person['name'])
    # print(len(res))
    return True if len(res)>0 else False

def add_persons(persons, bulk_size=1000):
    times = int(math.ceil(len(persons) / bulk_size))
    debug_logger.debug("Commit times: {}".format(times))
    for i in range(times):
        debug_logger.debug("times: {}/{}".format(i, times))
        tx = graph.begin()
        for person in persons[i*bulk_size:(i+1)*bulk_size]:
            if not exist(person):
                tx.create(Node("Person", **person))
            else:
                debug_logger.debug('\t {} existed.'.format(person['name']))
        tx.commit()


def add_relations():
    pass


def count_person_nodes():
    nodes = NodeMatcher(graph)
    return nodes.match("Person").count()


class BK_TEST(TestCase):

    def test_add_persons(self):
        entity_dict = all_entity_dict()
        i = 0
        persons = []
        for name, attrs in entity_dict.items():
            # if i>1001: break
            # i += 1
            p = {}
            p['name'] = name
            p['nicknames'] = attrs['nicknames']
            p['types'] = attrs['types']
            persons.append(p)
        print(len(persons))
        debug_logger.setLevel(logging.DEBUG)
        add_persons(persons)


    def test_exist(self):
        p = {"name": "一宇","types": ["明星"],"nicknames": []}
        exist(p)

    def test_count(self):
        print("Person counting: {}".format(count_person_nodes()))


    def test_search_extract(self):
        debug_logger.setLevel(logging.DEBUG)
        # art = search_all_do(ENTMT_ES_INDEX, 10)
        # for idx, art in enumerate(art):
        #     ts = extract_article(art, idx_document=idx)
        #     for t in ts:
        #         print(t)

        search_all_do(ENTMT_ES_INDEX, 100, extract_article)