from django.test import TestCase
from rest_framework import serializers
from EventExploreServer.model import ArticleES, TripleUnit


class ArticleESSerializer(serializers.Serializer):
   id = serializers.CharField()
   url = serializers.CharField()
   title = serializers.CharField()
   content = serializers.CharField()
   time = serializers.CharField()
   media_show = serializers.CharField()
   media_level = serializers.CharField()
   qscore = serializers.CharField()
   thumb = serializers.CharField()
   score = serializers.FloatField()


class TripleSerializer(serializers.Serializer):
    doc_num = serializers.IntegerField()
    sent_num = serializers.IntegerField()
    num = serializers.IntegerField()
    e1_lemma = serializers.CharField()
    relation_lemma = serializers.CharField()
    e2_lemma = serializers.CharField()



class TestSer(TestCase):

    def test_article_ser(self):
        art1 = ArticleES('001', 'http', 't', 'c', 'time', 'm', 1, 2, 'xxx', 1.3)
        art2 = ArticleES('002', 'http', 't', 'c', 'time', 'm', 1, 2, 'xxx', 1.3)
        ser = ArticleESSerializer(art1)
        print(ser.data)
        ser = ArticleESSerializer([art1, art2], many=True)
        print(ser.data)

    def test_triple_ser(self):
        from EventExploreServer.model import WordUnit
        e1 = WordUnit(1, '小明', 'n')
        rel = WordUnit(2, '去', 'v')
        e2 = WordUnit(3, '北京', 'n')

        t1 = TripleUnit(e1, rel, e2)
        ser = TripleSerializer(t1)
        print(ser.data)
