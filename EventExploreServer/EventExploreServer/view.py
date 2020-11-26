import json
import logging
from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from rest_framework.views import APIView
from EventExploreServer.component import search_articles
from EventExploreServer.model.serializers import ArticleESSerializer

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
    def get(self, request):
        pass

    def post(self, request):
        pass

class EventExplore(APIView):
    def get(self, request):
        pass

    def post(self, requet):
        pass
