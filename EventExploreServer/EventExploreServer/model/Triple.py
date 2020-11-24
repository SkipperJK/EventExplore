import unittest
import logging
from EventExploreServer.model.Word import WordUnit
debug_logger = logging.getLogger('debug')

class TripleUnit:

    class GeneralizationTriple:
        """
        一个元组可以泛化成多个元组
        """
        def __init__(self, num, doc_num, sent_num, arg1, rel, arg2):
            self.num = num
            self.doc_num = doc_num
            self.sent_num = sent_num
            self.arg1 = arg1
            self.rel = rel
            self.arg2 = arg2

        def get_triple(self):
            return '{:s},{:s},{:s}'.format(
                self.arg1.strip(),
                self.rel.strip(),
                self.arg2.strip()
            )

        def to_string(self):
            return "num: {}, doc: {}, sent: {} Triple: {}".format(
                self.num,
                self.doc_num,
                self.sent_num,
                str(self)
            )

        def __str__(self):
            # 使用中文空格 chr(12288) 填充，实现中文对齐
            return "({:s},{:s},{:s})".format(
                self.arg1,
                self.rel,
                self.arg2
            )


    def __init__(self, entity1_list, relationship_list, entity2_list, sent_num=0, doc_num=0, num=0):
        """
        关系三元组，entity和relationship由单个/多个word组成，将单个的也转换为list
        :param doc_num: int
        :param sent_num: int
        :param entity1_list: WordUnit list / WordUnit
        :param relationship_word: WordUnit list / WordUnit
        :param entity2_list: WordUnit list / WordUnit
        """
        self.doc_num = doc_num
        self.sent_num = sent_num
        self.num = num
        if isinstance(entity1_list, list):
            self.entity1_list = [entity for entity in entity1_list if entity]
        else:
            self.entity1_list = [entity1_list]
        if isinstance(relationship_list, list):
            self.relationship_list = [entity for entity in relationship_list if entity]
        else:
            self.relationship_list = [relationship_list]
        if isinstance(entity2_list, list):
            self.entity2_list = [entity for entity in entity2_list if entity]
        else:
            self.entity2_list = [entity2_list]

        debug_logger.debug('Entity 是什么：：：{},{}'.format(self.entity1_list, self.entity2_list))
        self.e1_lemma = ''.join([word.lemma for word in self.entity1_list])
        self.relation_lemma = ''.join([word.lemma for word in self.relationship_list])
        self.e2_lemma = ''.join([word.lemma for word in self.entity2_list])
        self.gts = self.generalization()

    def generalization(self):
        """
        关系元组一般化，
            1 记录元组中两个实体的命名实体类型
            2 将关系词简化，去掉介词 --- TODO
        :return:
        """
        self.entity1_nertype = ''
        self.entity2_nertype = ''
        nertag2type = {'Nh':'person', 'Ns':'location', 'Ni':'organization'}
        for entity in self.entity1_list:
            if entity.nertag:
                self.entity1_nertype = nertag2type[entity.nertag]
                break
        for entity in self.entity2_list:
            if entity.nertag:
                self.entity2_nertype = nertag2type[entity.nertag]
                break

        gts = []
        gts.append(self.GeneralizationTriple(self.num, self.doc_num, self.sent_num, self.e1_lemma, self.relation_lemma, self.e2_lemma))
        if self.entity1_nertype:
            gts.append(self.GeneralizationTriple(self.num, self.doc_num, self.sent_num, self.entity1_nertype, self.relation_lemma, self.e2_lemma))
        if self.entity2_nertype:
            gts.append(self.GeneralizationTriple(self.num, self.doc_num, self.sent_num, self.e1_lemma, self.relation_lemma, self.entity2_nertype))
        if self.entity1_nertype and self.entity2_nertype:
            gts.append(self.GeneralizationTriple(self.num, self.doc_num, self.sent_num, self.entity1_nertype, self.relation_lemma, self.entity2_nertype))
        return gts


    def to_string(self):
        return "Num:{0:>3d}, DocID: {1:>3d}, SentenceID: {2:>3d}, {3:s}".format(
            self.num,
            self.doc_num,
            self.sent_num,
            str(self)
        )


    def __str__(self):
        # 使用中文空格 chr(12288) 填充，实现中文对齐
        return "(E1: {0:{6}>10s}, Rel: {1:{6}>10s}, E2: {2:{6}>10s}), Generalization: <{3:s}>, {4:s}, <{5:s}>".format(
            self.e1_lemma,
            self.relation_lemma,
            self.e2_lemma,
            self.entity1_nertype if self.entity1_nertype else self.e1_lemma,
            self.relation_lemma,
            self.entity2_nertype if self.entity2_nertype else self.e2_lemma,
            chr(12288)
        )

    __repr__ = __str__  # 控制台输出时默认调用


class UniqueTriple:

    def __init__(self, arg1:str, rel:str, arg2:str, id:int=0):
        """
        每个triple都是唯一的。
        :param id: int
        :param arg1: str
        :param rel: str
        :param arg2: str
        """
        self.id = id
        self.arg1 = arg1
        self.rel = rel
        self.arg2 = arg2

    def to_string(self):
        return "{:d}:{:s}".format(self.id, str(self))

    def __str__(self):
        return "{:s},{:s},{:s}".format(self.arg1, self.rel, self.arg2)

    # 自定义__hash__,__eq__实现作为dict的key
    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)




class TESTTriple(unittest.TestCase):

    def test_seq(self):
        e1 = WordUnit(1, "美国", "nh")
        relationship = WordUnit(2, "总统", 'n')
        e2 = WordUnit(3, "特朗普", 'ni')
        t = TripleUnit(e1, relationship, e2, 0, 0)
        print(t)


        import json
        # JSON 序列化对象
        class TT:
            def __init__(self, name):
                self.name = name
        ## 1. 构造函数
        def obj_2_json(obj):
             return {
                 "name": obj.name
             }
        o = TT(name="aaa")
        json.dumps(o, default=obj_2_json)
        ## 2. 使用lambda
        json.dumps(o, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)


        # JSON反序列化对象
        json_str = '{"name":"tt"}'
        def handle(d):
            return TT(d['name'])
        json.loads(json_str, object_hook=handle)


    def test_unique_triple(self):
        ut = UniqueTriple('arg1', 'rel', 'arg2')
        uto = UniqueTriple('arg1', 'rel', 'arg2')
        print(ut)
        # 作为key
        d = dict()
        d[ut] = 10
        print(d[uto])