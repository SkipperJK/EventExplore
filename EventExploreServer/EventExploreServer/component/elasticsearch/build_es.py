from pymongo import MongoClient
from elasticsearch import Elasticsearch

from django.test import TestCase
from config import ES_HOST, ES_INDEX, ENTMT_ES_INDEX
from config import MONGODB_HOST, MONGODB_PORT, BULK_SIZE
from config import MONGODB_DATABASE_NAME, MONGODB_ARTICLE_COLLECTION, MONGODB_ENTMT_COLLECTION
from config import ES_FIELD_MAPPING, ENTMT_ES_FIELD_MAPPING
from EventExploreServer.component.elasticsearch.DB2ES import import_data2es
from EventExploreServer.component.elasticsearch.es_mappings import mappings, entmt_mapping


# 连接ES
es = Elasticsearch(ES_HOST)
print(es.cat.health())
# 连接db
db_connect = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
print(db_connect.server_info())
db = db_connect[MONGODB_DATABASE_NAME]


def build_es(index, es_mapping, mongo_coll, bulk_size, field_mapping):
    """
    建立索引并导入数据
    :param index:
    :param es_mapping:
    :param mongo_coll:
    :param bulk_size:
    :param field_mapping:
    :return:
    """
    es.indices.create(index=index, body=es_mapping)
    collection = db[mongo_coll]
    import_data2es(es, index, collection, bulk_size, field_mapping)


class TestESOp(TestCase):

    def test_mongodb(self):
        db_connect = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
        db = db_connect[MONGODB_DATABASE_NAME]
        coll = db[MONGODB_ENTMT_COLLECTION]
        print(coll.find().count())
        print(coll.find(skip=10000, limit=100).count())
        print(coll.find(skip=1787900, limit=100).count())
        # print(coll.find(skip=1787900, limit=100).size())
        print(coll.find().skip(10000).limit(100).count())
        print(coll.find().skip(10000).limit(100).count())
        print(coll.count_documents({}, skip=1000, limit=100))
        for art in coll.find(skip=1787900, limit=100):
            print(art)

    def test_delete_index(self):
        index = 'sina_article_entmt'
        es.indices.delete(index=index)

    def test_add_index(self):
        index = ENTMT_ES_INDEX
        mappings = entmt_mapping
        coll = MONGODB_ENTMT_COLLECTION
        bulk_size = BULK_SIZE
        field_mapping = ENTMT_ES_FIELD_MAPPING
        build_es(index, mappings, coll, bulk_size, field_mapping)



if __name__ == '__main__':
    # 全品类数据
    build_es(ES_INDEX, mappings, MONGODB_ARTICLE_COLLECTION, BULK_SIZE, ES_FIELD_MAPPING)
    # 娱乐数据
    build_es(ENTMT_ES_INDEX, entmt_mapping, MONGODB_ENTMT_COLLECTION, BULK_SIZE, ENTMT_ES_FIELD_MAPPING)

    # build_es("test_index", entmt_mapping, MONGODB_ENTMT_COLLECTION, BULK_SIZE, ENTMT_ES_FIELD_MAPPING)
    # es.indices.delete(index='test_index')

