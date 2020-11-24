from elasticsearch import Elasticsearch
from config import ES_HOST, ES_INDEX


es = Elasticsearch(ES_HOST)
print(es.cat.health())


# 索引分为5个分片
mappings = {
  "settings": {
    "number_of_shards" : 5,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "id": {
        "type": "text"
      },
      "url": {
        "type": "text"
      },
      "time":{
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
      },
      "title":{
        "type":"text",
        "analyzer": "index_ansj",
        "search_analyzer": "query_ansj"
      },
      "content":{
        "type":"text",
        "analyzer": "index_ansj",
        "search_analyzer": "query_ansj"
      },
      "media_show":{
        "type": "text"
      },
      "media_level":{
        "type": "integer"
      },
      "qscore":{
        "type": "integer"
      },
      "thumb":{
        "type": "text"
      }
    }
  }
}

es.indices.create(index=ES_INDEX, body=mappings)
# es.indices.delete(index='sina')
# es.indices.delete(index='.kibana_1')