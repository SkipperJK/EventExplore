import json
import logging
from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from rest_framework.views import APIView
from EventExploreServer.component import search_articles
from EventExploreServer.component import extract_text
from EventExploreServer.component.word_link.explore import explore
from EventExploreServer.model.serializers import ArticleESSerializer, TripleSerializer

trace_logger = logging.getLogger('trace')

"""
Django提供的模版系统，解耦视图和模版之间的硬连接
    1 使用基础的template
    2 使用快捷方式 render
"""

def index(request):
    # return HttpResponse("The first view.")
    context = {}
    # template = loader.get_template('index.html')
    # return HttpResponse(template.render(context, request))
    return render(request, 'index.html')
    # gdata = {
    #     "results": [
    #         {
    #             "columns": ["user", "entity"],
    #             "data": [
    #                 {
    #                     "graph": {
    #                         "nodes": [
    #                             {
    #                                 "id": "1",
    #                                 "labels": ["User"],
    #                                 "properties": {
    #                                     "userId": "eisman"
    #                                 }
    #                             },
    #                             {
    #                                 "id": "8",
    #                                 "labels": ["Project"],
    #                                 "properties": {
    #                                     "name": "neo4jd3",
    #                                     "title": "neo4jd3.js",
    #                                     "description": "Neo4j graph visualization using D3.js.",
    #                                     "url": "https://eisman.github.io/neo4jd3"
    #                                 }
    #                             }
    #                         ],
    #                         "relationships": [
    #                             {
    #                                 "id": "7",
    #                                 "type": "DEVELOPES",
    #                                 "startNode": "1",
    #                                 "endNode": "8",
    #                                 "properties": {
    #                                     "from": 1470002400000
    #                                 }
    #                             }
    #                         ]
    #                     }
    #                 }
    #             ]
    #         }
    #     ],
    #     "errors": []
    # }
    # return HttpResponse(gdata)

def echart_test(request):
    return render(request, 'echart.html')

def search_relative_articles(request, topic):
    trace_logger.info("searching {} relative article".format(topic))
    articles = search_articles(topic)
    return HttpResponse(json.dumps(articles, default=lambda obj: obj.__dict__))


class SearchView(APIView):
    def get(self, request, topic):
        articles = search_articles(topic)
        return HttpResponse(ArticleESSerializer(articles, many=True).data)


    def post(self, request):
        pass


class OpenIEView(APIView):
    def get(self, request, text):
        trace_logger.info("Input text: {}".format(text))
        triples = extract_text(text)
        triple_ser = []
        for triples_of_sent in triples:
            triple_ser.append(TripleSerializer(triples_of_sent, many=True).data)
        # return HttpResponse(TripleSerializer(triples, many=True).data)
        return HttpResponse(triple_ser)
        pass

    def post(self, request):
        pass

class EventExplore(APIView):
    def get(self, request, topic):
        trace_logger.info("EventExplore ----- Topic: {} -----".format(topic))
        return HttpResponse(json.dumps("ttttt"))
        articles = search_articles(topic)
        data = explore(articles)
        print('-------', data)
        return HttpResponse(json.dumps(data))

    def post(self, requet):
        pass
