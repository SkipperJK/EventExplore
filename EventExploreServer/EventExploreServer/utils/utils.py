import re
import unittest


def split_sentence(content):
    content = content.replace("\t", "")
    content = content.replace(" ", "")
    content = re.sub('([。！？\?])([^”’])', r"\1\n\2", content)  # 单字符断句符, [^"']中括号中的^表示非。
    content = re.sub('(\.{6})([^”’])', r"\1\n\2", content)  # 英文省略号
    content = re.sub('(\…{2})([^”’])', r"\1\n\2", content)  # 中文省略号
    # content = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', content)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    content = content.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    sentences = content.split("\n")
    ret_sents = []
    for sent in sentences:
        sent.replace("\t", "").replace("\n", "").replace(" ", "")
        if sent: ret_sents.append(sent)
    return ret_sents


def find_sub_obj(trigger, words):
    sub = None
    obj = None
    trigger_id = trigger['id']
    for i, word in enumerate(words):
        if i+1 == trigger_id:
            continue
        if word['head_id'] == trigger_id:
            if word['dependency'] == '主谓关系' and word['postag'][0] == 'n':
                sub = word
            elif word['dependency'] == '动宾关系' and word['postag'][0] == 'n':
                obj = word
    return sub, obj


def is_entity(word):
    """
    判断一个词是否是指定的实体类型
    :param entry: WordUnit
    :return:
    """
    # 候选实体词性列表
    # 人名，机构名，地名，其他名词，缩略词 --- 添加：时间名词nt    TODO; 后面添加更多可能的实体类型，数字等等
    # entity_postags = {'nh', 'ni', 'ns', 'nz', 'j', 'nt', 'nl'} # nl 位置名词
    postags = {'nh', 'ni', 'ns', 'nz', 'j'}
    if word.postag in postags:
        return True
    else:
        return False


def is_named_entity(word):
    """
            判断一个词是否是 人名，地名，机构名 三种命名实体类型
            :param entry:  WordUnit
            :return:
            """
    postags = {'nh', 'ni', 'ns', 'nz'}
    nertags = {'Nh', 'Ns', 'Ni'}

    if (word.postag in postags) or (word.nertag in nertags):
        return True
    else:
        return False


class TestUtils(unittest.TestCase):

    def test_split_sentence(self):
        text = "老年痴呆症的发病比例比普通人想象的大得多。据英国国家医疗服务系统的统计数据显示，65岁以上老年人患痴呆症的比例约为7%，80岁以上老人患病比例约为16.6%。确诊一个人是否患上痴呆症不太容易，因为每个人最初的症状不太一样。为了方便蛋友自吓自诊，下面是9个可能患有痴呆症的早期表现：时间观念减弱和路痴痴呆患者的时间观念和识路能力会变弱。比如有的人身在超市，却忘了自己是怎么过去的，还有，你突然问一个人今天是星期几，或者几月几号，他会一时想不起来。提笔忘字这一点和上边那点很像，痴呆症会让人变得“提笔忘字”。比如用笔写出自己的收货地址，写封信之类的，你会发现很难写出想表达的词或者句子；而且你还会发现，在写东西的时候心绪杂乱，很难集中注意力－－痴呆症初期阶段的人就是这样，无法长时间集中精神于一点－－你可以在看完这篇文章之后马上找张纸写点什么感受一下。短期记忆出问题痴呆症最常见的早期症状是短期记忆出现问题。当然每个人都有那种忘了把钱包或者手机放在什么地方的时候，但痴呆症不同，它会让这种“小健忘”变得更严重，也更频繁：东西会奇怪地放在它不该放的地方，比如在鞋垫里发现零钱，在衣橱里发现U盘。情绪波动早期痴呆症常导致情绪波动和日常行为的改变，这种情绪变化是无缘无故的，一个人刚刚还是好好的，下一刻就突然大笑，或者突然哭泣，那真的要小心了。交流困难对于痴呆症患者来说，很难找到合适的词语表达自己的想法－－这并不是说那个想法很复杂，需要高深的词－－通常他们记不住的是一个人的名字或者日常用品的名字。和一个可能患有痴呆症的人聊天是很别扭的，你会发现他经常把天聊死。重复痴呆症早期病人会经常重复说自己说过的话。他会用同样的语气一遍又一遍地说同一件事，或者一遍又一遍地问同样的问题。这种重复不仅发生在谈话中，在做事情时也会发生。无精打采，萎靡不振一个很阳光的朋友忽然頽了？不再勇往直前了？这可能是早期痴呆症的症状。相似的症状还有：对以前很喜欢的活动或者爱好不再热情了、精力不如从前了、睡得比平时多、经常感到累，无精打采，整个人仿佛被掏空。注意力下降注意力降低也是痴呆患者的一个常见症状。另外痴呆症会让一个人解决问题的能力或者组织能力、计划能力下降，从而显得做起事情来没有规划，乱做一通。重复痴呆症早期病人会经常重复说自己说过的话。他会用同样的语气一遍又一遍地说同一件事，或者一遍又一遍地问同样的问题。这种重复不仅发生在谈话中，在做事情时也会发生。做家务变得困难起来日常家务会因为痴呆症变得困难起来。平常的扫地、做饭、洗衣服，突然间变成了“不可能完成的任务”，这种初期症状表现为，一个人不知道应该先做什么后做什么，或者从何处下手开始做家务。本文译自 tips-and-tricks.co，由译者 暴雨里的水 基于创作共用协议(BY-NC)发布。"
        sentences = split_sentence(text)
        for sent in sentences:
            print(sent)