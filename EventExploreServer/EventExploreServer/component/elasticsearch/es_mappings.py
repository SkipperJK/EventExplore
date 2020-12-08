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


entmt_mapping = {
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties":{
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
      "imgs": {
        "type": "text"
      },
      "source":{
        "type": "text"
      },
      "channel":{
        "type": "text"
      },
      "types": {
        "type": "text"
      },
      "tags": {
        "type": "text"
      }
    }
  }
}
