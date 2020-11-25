import json
import logging
from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse
from EventExploreServer.component import search_articles

trace_logger = logging.getLogger('trace')

"""
Django提供的模版系统，解耦视图和模版之间的硬连接
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