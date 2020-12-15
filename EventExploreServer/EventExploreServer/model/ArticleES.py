from collections import namedtuple
from EventExploreServer.utils.utils import split_sentence

class ArticleES:

    def __init__(self, id, url, title, content, time,
                 media_show=None, media_level=None, qscore=None, thumb=None,
                 imgs=None, source=None, channel=None, types=None, tags=None,
                 score=0):
        """
        ES召回的文章对象
        :param id: int
        :param url: str
        :param title: str
        :param content: str
        :param time: str
        :param media_show: str
        :param media_level: str TODO; 索引返回是str
        :param qscore: str TODO; 索引返回是str
        :param thumb: str
        :param score: float
        """
        self.id = id
        self.url = url
        self.title = title
        self.content = content
        self.time = time
        self.media_show = media_show
        self.media_level = media_level
        self.qscore = qscore
        self.thumb = thumb
        self.imgs = imgs
        self.source = source
        self.channel = channel
        self.types = types
        self.tags = tags
        self.score = score



    @property
    def sentence_of_title(self):
        return split_sentence(self.title)

    @property
    def sentence_of_content(self):
        return split_sentence(self.content)




def customAritcleESDecoder(articleDict):
    """
    convert json(str) to ArticleES object
    :param articleDict:
    :return:
    """
    return namedtuple("ArticleES", articleDict.keys())(*articleDict.value())
    # namedtuple是一个函数，相当于执行函数返回函数的返回值