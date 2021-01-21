import json
import logging
from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from rest_framework.views import APIView
from rest_framework.response import Response
from EventExploreServer.model import TripleUnit
from EventExploreServer.component import extract_text, exact_search_articles
from EventExploreServer.component.word_link.explore import explore
from EventExploreServer.model.serializers import ArticleESSerializer, TripleSerializer, SentenceSerializer
from EventExploreServer.component import annotate_text,annotate_sentence
from EventExploreServer.component import extract_rules

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
    articles = exact_search_articles(topic)
    return HttpResponse(json.dumps(articles, default=lambda obj: obj.__dict__))


class MainView(APIView):
    def get(self, request):
        return render(request, 'main.html')

    def post(self, request):
        pass


class SearchView(APIView):
    def get(self, request, topic):
        articles = exact_search_articles(topic)
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
        articles = exact_search_articles(topic)
        data = explore(articles)
        print('-------', data)
        return HttpResponse(json.dumps(data))

    def post(self, request):
        pass


class OpenREView(APIView):
    def get(self, request, text):
        pass

    def post(self, request):
        pass


class AnnotateView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        trace_logger.info("对待标注文本进行处理...")
        query = dict(request.data)
        trace_logger.info("提交的内容: {}".format(query))
        sentences = annotate_text(query['text'])
        jsonData = SentenceSerializer(sentences, many=True).data
        trace_logger.info("返回处理之后的内容: {} 给前端。".format(jsonData))
        return Response(jsonData)



class LabelView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        labeled_data = dict(request.data)
        trace_logger.info("处理提交的标注信息：{}".format(labeled_data))
        sentence = annotate_sentence(labeled_data['origin_sentence'])
        triples = []
        for triple in labeled_data['triples']:
            entity1_list = [sentence.words[idx] for idx in triple['idx_e1']]
            relation_list = [sentence.words[idx] for idx in triple['idx_rel']]
            entity2_list = [sentence.words[idx] for idx in triple['idx_e2']]
            t = TripleUnit(entity1_list, relation_list, entity2_list)
            triples.append(t)

        extract_rules(triples, sentence)
        # rules = extract_rules(triples, sentence)
        # for rule in rules:
        #     trace_logger.info("Rule: "+rule.to_string())

        # 根据标记信息提取规则
        retData = "Successed"
        trace_logger.info("抽取标注数据规则完成。")

        return Response(retData)