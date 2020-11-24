#!/usr/bin/env bash
PUT /sina ' 
{
  "settings": {
    "number_of_shards" : 5,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
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
      }
    }
  }
}
'