from django.test import TestCase
from rest_framework import serializers
from EventExploreServer.model import ArticleES, Triple


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
    pass




class TestSer(TestCase):

    def test_ser(self):
        art1 = ArticleES('001', 'http', 't', 'c', 'time', 'm', 1, 2, 'xxx', 1.3)
        art2 = ArticleES('002', 'http', 't', 'c', 'time', 'm', 1, 2, 'xxx', 1.3)
        ser = ArticleESSerializer(art1)
        print(ser.data)
        ser = ArticleESSerializer([art1, art2], many=True)
        print(ser.data)