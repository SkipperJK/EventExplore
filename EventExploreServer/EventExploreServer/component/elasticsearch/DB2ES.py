from pymongo import MongoClient
from elasticsearch import helpers
from elasticsearch import Elasticsearch
from config import ES_HOST, ES_INDEX, ES_FIELD_MAPPING, BULK_SIZE
from config import MONGODB_HOST, MONGODB_PORT, MONGODB_DATABASE_NAME, MONGODB_ARTICLE_COLLECTION

# 连接db
db_connect = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
# test connection of db
print(db_connect.server_info())

db = db_connect[MONGODB_DATABASE_NAME]
collection = db[MONGODB_ARTICLE_COLLECTION]

# 可能需要索引建立加速导入
# 连接es
es = Elasticsearch(ES_HOST)
# test connection of es
print(es.cat.health())


# 导入数据
cnt = 0
cnt_all = 0
actions = []
all_time = 0
for doc in collection.find().batch_size(BULK_SIZE):
    doc['_id'] = str(doc['_id'])
    action = {}
    action = {
        "_op_type": "create",
        "_index": ES_INDEX,
        "_id": str(doc["_id"]),
        "_source": {}
    }
    for key, value in ES_FIELD_MAPPING.items():
        if key in doc:
            action["_source"][value] = doc[key]
        else:
            action["_source"][value] = {}

    # add in doc
    actions.append(action)
    if cnt_all != 0 and cnt_all % BULK_SIZE == 0:
        try:
            helpers.bulk(es, actions=actions)
            print("Put successfully. Bulk " + str(cnt_all//BULK_SIZE))
        except Exception as e:
            print(e)
            print("Got redundent items. Bulk " + str(cnt_all//BULK_SIZE))
        del actions[0:len(actions)]
    cnt_all += 1

if len(actions) != 0:
    try:
        helpers.bulk(es, actions=actions)
    except Exception as e:
        print("Got redundent items.")

print("Finished." + str(cnt_all))
