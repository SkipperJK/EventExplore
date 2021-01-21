import json
import logging
from django.test import TestCase
from config import ES_HOSTS, ES_INDEX
import jieba.posseg as pseg
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from EventExploreServer.model import ArticleES

es = Elasticsearch(ES_HOSTS)
debug_logger = logging.getLogger('debug')
root_logger = logging.getLogger('root')
trace_logger = logging.getLogger('trace')

def search_all_do(index, size=10, func=None, func_return_type='list'):
    """
    检索指定索引中的所有文章，如果指定func，则对每篇文章执行func
    :param index:
    :param size: None表示全部，数字表示指定文章数量
    :param func:
    :return:
    """
    action = {
        "query": {
            "match_all": {}
        }
    }
    articles = []
    rets = []
    if func and func_return_type == 'dict':
        rets = {}

    resps = scan(es, action, scroll="1000m", index=index)
    count = 0
    try:
        for item in resps:
            if size and count >= size: break
            # score = item['_score']
            source = item['_source']
            trace_logger.info("Num: {}, Article Title: {}".format(count, source['title']))
            art = ArticleES(**source)
            articles.append(art)
            if func:
                ret = func(art)
                if isinstance(ret, list):
                    rets += ret
                elif isinstance(ret, dict):
                    for key, value in ret.items():
                        if key not in rets:
                            rets[key] = value
                else:
                    ret.append(ret)
            count += 1
    except Exception as e:
        root_logger.info("ES indexing error : {}".format(e))
    if func:
        return rets
    else:
        return articles


def search_articles(text, index, size):

    action = {
        "size": size,
        "query": {
            "bool": {
                "must": [
                    {"match": {"title": text}}
                ],
                "should": [
                    {"match": {"content": text}}
                ]
            }
        }
    }

    response = es.search(body=action, index=index)
    articles = []
    for articleDict in response["hits"]["hits"]:
        score = articleDict['_score']
        source = articleDict['_source']
        source['score'] = score
        articles.append(ArticleES(**source))
    return articles



def exact_search_articles(topic ='', size=10000, index=ES_INDEX):
    """
    TODO 有三种，title和content
    TODO; 通过词性标注/命名体识别来决定要不要must match
    :param topic:
    :param size:
    :return:
    """
    allow_pos = [
        'n', 'nr', 'nz', 'ns', 'v', 't', 's', 'nt', 'nw', 'vn' 
        'PER', 'LOC', 'ORG', 'TIME'
    ]
    keywords = []
    # for word in jieba.cut(topic):
    #     keywords.append(word)
    for word, flag in pseg.cut(topic):
        if flag in allow_pos:
            keywords.append(word)
    # seg = pkuseg.pkuseg(model_name='news', postag=True)
    # for item in seg.cut(topic):
    #     if item[1] in allow_pos:
    #         keywords.append(item[0])

    action = {
        "size":size,
        "query":{
            "bool": {
                "must":[
                ]
            }
        }
    }

    for word in keywords:
        action["query"]["bool"]["must"].append({'match': {"title": word}})
    root_logger.info(action)

    response = es.search(body=action, index=index) # ES返回的是dict类型，
    articles = []
    for articleDict in response["hits"]["hits"]:
        # articles.append(ArticleES(**articleDict['_source']))
        score = articleDict['_score']
        source = articleDict['_source']
        source['score'] = score
        articles.append(ArticleES(**source))
        # articles.append(ArticleES(source['title'], source['content'], source['time'], score))
    # find_point([art.score for art in articles])
    return articles



def find_point(scores):
    debug_logger.debug(scores)
    import matplotlib.pyplot as plt
    plot_objs = plt.subplots(nrows=3, ncols=1, figsize=(12, 6))
    print(plot_objs)
    fig, (ax1, ax2, ax3) = plot_objs
    ax1.plot(scores)
    slopes = []
    diffs = []
    for i in range(0, len(scores)-1):
        slopes.append(scores[i+1]-scores[i])
        diffs.append(scores[i+1]-scores[i])
    debug_logger.debug(slopes)
    debug_logger.debug(diffs)
    ax2.plot(slopes)
    ax3.plot(diffs)
    plt.show()


class TESTES(TestCase):

    def test_search_all(self):
        from config import ENTMT_ES_INDEX
        arts = search_all_do(ENTMT_ES_INDEX)
        print(len(arts))


    def test_search(self):
        text = "奥斯卡提名"
        from config import ENTMT_ES_INDEX
        arts = search_articles(text, ENTMT_ES_INDEX, 100)
        debug_logger.setLevel(logging.DEBUG)
        for idx, art in enumerate(arts):
            debug_logger.debug(art.__dict__)


    def test_extract_search(self):
        topic = '中国'
        topic = '吴昕金牛座男友'
        topic = "马航MH370"
        topic = "艾塞罗比亚"
        topic = "埃塞俄比亚"
        topic = '奥斯卡提名'
        articles = exact_search_articles(topic, 200)
        scores = []
        debug_logger.setLevel(logging.DEBUG)
        for idx, article in enumerate(articles):
            debug_logger.debug("idx: {},id: {} score: {} title: {}".format(idx, article.id, article.score, article.title))
            debug_logger.debug(article.__dict__)
            scores.append(article.score)
            # print(article.__dict__)
            # debug_logger.debug(article.__dict__)

    def test_from_size_search(self):
        from config import ENTMT_ES_INDEX
        action = {
            "query": {
                "match_all": {}
            },
            "size": 10,
            "from": 100000
        }

        # res = es.search(body=action, index=ES_INDEX)
        res = es.search(body=action, index=ENTMT_ES_INDEX)
        for item in res['hits']['hits']:
            source = item['_source']
            print(source['title'])

        # print('search_all_do')
        # arts = search_all_do(ENTMT_ES_INDEX, 5)
        # for art in arts:
        #     print(art.title)

    '''ES return item
    {
        '_index': 'sina_article_20191121', 
        '_type': '_doc', 
        '_id': '5f57634b83577eadc453f7c9', 
        '_score': 10.074459, 
        '_source': {
            'time': '2019-10-01 13:50:19', 
            'title': '中国色彩，中国味道，中国红，中国创意。', 
            'content': '中国色彩，中国味道，中国红，中国创意。
        }
    }
    '''