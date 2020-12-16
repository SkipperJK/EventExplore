import logging
from EventExploreServer.model.Word import WordUnit
from EventExploreServer.model.Triple import TripleUnit
from EventExploreServer.utils.utils import is_entity, is_named_entity

debug_logger = logging.getLogger('debug')
class ExtractByDSNF:
    """
    对每个entity pair，根据DSNF(Dependency Semantic Normal Forms)进行知识抽取
    Attributes:
        origin_sentence: str，原始句子
        sentence: WordUnit list，依存句法分析之后构成的句子
        entity1: WordUnit
        entity2: WordUnit
        head_relation:
        triple:
    """
    # origin_sentence = ''  # str，原始句子
    # sentence = None  # SentenceUnit，句子表示，每行为一个词
    # entity1 = None  # WordUnit，实体1词单元
    # entity2 = None  # WordUnit，实体2词单元
    # head_relation = None  # WordUnit，头部关系词单元
    #triples = []
    # file_path = None  # Element，XML文档
    # num = 1  # 三元组数量编号

    # def __init__(self, origin_sentence, sentence, entity1, entity2, file_path, num):
    def __init__(self, origin_sentence, sentence, entity1, entity2, idx_sentence=0, idx_document=0, num=0):
        self.origin_sentence = origin_sentence
        self.sentence = sentence
        self.entity1 = entity1
        self.entity2 = entity2
        self.idx_sentence = idx_sentence
        self.idx_document = idx_document
        self.num = num
        self.center_word_of_e1 = None   # 偏正结构的中心词
        self.center_word_of_e2 = None   # 偏正结构的中心词
        # self.file_path = file_path
        # self.num = num
        self.triples = []
        self.expand_entity()    # 处理e1，e2偏正结构
        debug_logger.debug('偏正结构对应的中心词：E1: {:s}, E2: {:s}'.format(
            str(self.center_word_of_e1),
            str(self.center_word_of_e2)
        ))
        # debug_logger.debug(sentence.nertags)
        #debug_logger.debug(sentence.is_extract_by_ne)

    # def is_entity(self, entry):
    #     """
    #     判断一个词是否是指定的实体类型
    #     :param entry: WordUnit
    #     :return:
    #     """
    #     # 候选实体词性列表
    #     # 人名，机构名，地名，其他名词，缩略词
    #     postags = {'nh', 'ni', 'ns', 'nz', 'j'}
    #     if entry.postag in postags:
    #         return True
    #     else:
    #         return False
    #
    # def is_named_entity(self, entry):
    #     """
    #     判断一个词是否是 人名，地名，机构名 三种命名实体类型
    #     :param entry:  WordUnit
    #     :return:
    #     """
    #     postags = {'nh', 'ni', 'ns'}
    #     nertags = {'Nh', 'Ns', 'Ni'}
    #
    #     if (entry.postag in postags) or (entry.nertag in nertags):
    #         return True
    #     else:
    #         return False

    def check_entity(self, entity):
        """偏正短语：由修饰语和中心语组成，结构成分之间有修饰与被修饰关系的短语。（往往修饰词是命名实体）
        处理偏正结构(奥巴马总统)，得到偏正部分(总统)，句子成分的主语或宾语 (中文普遍独特现象）
           奥巴马<-(ATT)-总统
           例如：奥巴马 总统 访问 中国。其中：奥巴马的偏正部分是 总统，总统在dp中和访问（verb）是SBV关系。
           "the head word is a entity and modifiers are called the modifying attributives"
           偏差修正构成NE，则进行标记。 例如：同济大学，对同济偏差修正（同济修饰大学）之后得到同济大学，同时同济大学NER标注为命名实体
           问题？？？？ --》 习近平主席：习近平修饰主席，但是习近平就是命名实体。后期修改：根据pos提取会有问题？因为会把主席这个词置为True
           #Solution： 其实不用判断是否是 机构实体 ，只需要对偏正结构标记即可，从而避免对偏正结构进行重复的关系元组提取。
           NOTE: 如果不存在偏正结构，就返回entity本身。
           NOTE: 最多返回entity的上一级修正中心
        Args:
            entity: WordUnit，待检验的实体
        Returns:
            head_word or entity: WordUnit，检验后的实体
        """
        head_word = entity.head_word  # 如果是偏正短语，则head_word就是中心词
        if entity.dependency == 'ATT':
            if self.like_noun(head_word) and abs(entity.ID - head_word.ID) == 1:
                # 处理机构命名实体分词被拆分情况，防止多次抽取
                # start = min(entity.ID, head_word.ID)
                # end = max(entity.ID, head_word.ID)
                # debug_logger.debug((start, end))
                # if (start-1, end-1) in [(item[1], item[2]) for item in self.sentence.nertags]:
                #     self.sentence.is_extract_by_ne[head_word.ID-1] = True
                # 标记所有的偏正部分，而不只是 机构命名实体
                self.sentence.has_extracted[head_word.ID-1] = True
                return head_word
            else:
                return entity
                # return None
        else:
            return entity
            # return None

    def expand_entity(self):
        self.center_word_of_e1 = self.check_entity(self.entity1)
        self.center_word_of_e2 = self.check_entity(self.entity2)


    def search_entity(self, modify):
        """根据偏正部分(也有可能是实体)找原实体
        Args:
            word: WordUnit，偏正部分或者实体
        Returns:
        """
        for word in self.sentence.words:
            if word.head == modify.ID and word.dependency == 'ATT':
                return word
        return modify


    def find_final_entity(self, entity):
        """
        找entity所在偏正结构的最终作为主语/宾语的实体
        :param word:  WordUnit
        :return: WordUnit
        """
        if entity.dependency == 'SBV' or entity.dependency == 'VOB':
            return entity

        word_tmp = entity
        while word_tmp.dependency == 'ATT':
            word_tmp = word_tmp.head_word
        return word_tmp if word_tmp else entity



    def like_noun(self, entry):
        """近似名词，根据词性标注判断此名词是否职位相关
        Args:
            entry: WordUnit，词单元
        Return:
            *: bool，判断结果，职位相关(True)，职位不相关(False)
        """
        #  'n'<--->general noun 普通名词        'i'<--->idiom 成语                       'j'<--->abbreviation 缩写词
        # 'ni'<--->organization name 机构名称   'nh'<--->person name 人名                'nl'<--->location noun 位置名词
        # 'ns'<--->geographical name 地名      'nz'<--->other proper noun 其他专有名词    'ws'<--->foreign words
        noun = {'n', 'i', 'j', 'ni', 'nh', 'nl', 'ns', 'nz', 'ws'}
        if entry.postag in noun:
            return True
        else:
            return False

    def get_entity_num_between(self, entity1, entity2):
        """获得两个实体之间的实体数量
        Args:
            entity1: WordUnit，实体1
            entity2: WordUnit，实体2
        Returns:
            num: int，两实体间的实体数量
        """
        num = 0
        i = entity1.ID + 1
        while i < entity2.ID:
            if is_named_entity(self.sentence.words[i]):
                num += 1
            i += 1
        return num

    def build_triple(self, entity1, entity2, relation, type="Other"):
        """建立三元组，写入json文件
        Args:
            entity1: WordUnit list，实体1
            entity2: WordUnit list，实体2
            relation: WordUnit list，关系列表
            num: int，知识三元组编号
        Returns:
            True: 获得三元组(True)
        """
        self.triples.append(TripleUnit(entity1, relation, entity2, self.idx_sentence, self.idx_document, self.num))
        self.num += 1
        triple = dict()
        # triple['num'] = self.num
        # self.num += 1
        triple['origin_sentence'] = self.origin_sentence
        entity1_str = self.element_connect(entity1)
        entity2_str = self.element_connect(entity2)
        relation_str = self.element_connect(relation)
        triple['knowledge'] = [entity1_str, relation_str, entity2_str]
        debug_logger.debug('triple: ' + entity1_str + '\t' + relation_str + '\t' + entity2_str)
        return True

    def element_connect(self, element):
        """三元组元素连接
        Args:
            element: WordUnit list，元素列表
        Returns:
            element_str: str，连接后的字符串
        """
        element_str = ''
        if isinstance(element, list):
            for ele in element:
                if isinstance(ele, WordUnit):
                    element_str += ele.lemma
        else:
            element_str = element.lemma
        return element_str

    def SBV_CMP_POB(self, entity1, entity2):
        # TODO; 考虑并列主语或者宾语的情况
        """IVC(Intransitive Verb Construction)[DSNF4]
            不及物动词结构的一种形式，例如："奥巴马毕业于哈弗大学"--->"奥巴马 毕业 于 哈弗 大学"
            经过命名实体后，合并分词结果将是"奥巴马 毕业 于 哈弗大学"
            entity1--->"奥巴马"    entity2--->"哈弗大学"
        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        # ent1 = self.check_entity(entity1)  # 该实例对应为"奥巴马"
        # # 该实例对应为"哈弗大学"，
        # # 但当"哈弗"的命名实体识别为"S-Ni"时，命名实体识别后将是："哈弗 大学"，因为：哈弗<-[ATT]-大学
        # # 得到的将是["奥巴马", "毕业于", "哈弗大学"]
        # ent2 = self.check_entity(entity2)
        # debug_logger.debug('SBV_CMP_POB - 偏正修正部分：e1:{}, e2:{}'.format(ent1.lemma, ent2.lemma))
        ent1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        ent2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2
        if ent2.dependency == 'POB' and ent2.head_word.dependency == 'CMP':
            if ent1.dependency == 'SBV' and ent1.head == ent2.head_word.head:
                relations = []  # 实体间的关系
                relations.append(ent1.head_word)  # 该实例对应为"毕业"
                relations.append(ent2.head_word)  # 该实例对应为"于"
                debug_logger.debug("-"*10+"Intransitive Verb DSNF4"+'-'*10)
                return self.build_triple(entity1, entity2, relations)
                # print(entity1.lemma + '\t' + relations[0].lemma + relations[1].lemma + '\t' + entity2.lemma)
        return False

    def SBV_VOB(self, entity1, entity2, entity1_coo=None, entity2_coo=None, entity_flag=''):
        """TV(Transitive Verb)
            全覆盖[DSNF2|DSNF7]，部分覆盖[DSNF5|DSNF6]
            7：动词并列的情况   5和6：entity并列的左右附加情况
        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
            entity_coo: WordUnit，实际的并列实体
            entity_flag: str，实际并列实体的标志，并列主语还是并列宾语
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        type2 = "DSNF2"
        type5 = "DSNF5"
        type6 = "DSNF6"
        type7 = "DSNF7"
        # ent1 = self.check_entity(entity1)  # 偏正部分，若无偏正部分则就是原实体
        # ent2 = self.check_entity(entity2)
        # debug_logger.debug('SBV_VOB - 偏正修正部分：e1:{}, e2:{}'.format(ent1.lemma, ent2.lemma))
        ent1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        ent2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2

        entity1_list = []
        entity2_list = []
        entity1_list.append(entity1)
        entity2_list.append(entity2)
        # 处理多级修饰
        if ent1 != entity1 and abs(ent1.ID - entity1.ID) == 1:
            entity1_list.append(ent1)
            if ent1.dependency == 'ATT' and abs(ent1.head - entity1.ID) <= 3:
                entity1_list.append(ent1.head_word)
        if ent2 != entity2 and abs(ent2.ID - entity2.ID) == 1:
            entity2_list.append(ent2)
            if ent2.dependency == 'ATT' and abs(ent2.head - entity2.ID) <= 3:
                entity2_list.append(ent2.head_word)


        # 问题：是进入到determin中判断是否符合SBV_VOB结构的。。。。。。
        satisfy = False
        verbs = []
        if entity_flag == '':
            print('SVB_VOB Normal')
            e1_final = self.find_final_entity(entity1)
            e2_final = self.find_final_entity(entity2)
            if e1_final.dependency == 'SBV' and e2_final.dependency == 'VOB':
                verbs = self.determine_relation_SVB(entity1, entity2)
        elif entity_flag == 'subject' and entity1_coo:
            print('SVB_VOB sub coo')
            e1_coo_final = self.find_final_entity(entity1_coo)
            e2_final = self.find_final_entity(entity2)
            if e1_coo_final.dependency == 'SBV' and e2_final.dependency == 'VOB':
                verbs = self.determine_relation_SVB(entity1_coo, entity2)
        elif entity_flag == 'object' and entity2_coo:
            print('SVB_VOB obj coo')
            e1_final = self.find_final_entity(entity1)
            e2_coo_final = self.find_final_entity(entity2_coo)
            if e1_final.dependency == 'SBV' and e2_coo_final.dependency == 'VOB':
                verbs = self.determine_relation_SVB(entity1, entity2_coo)
        elif entity_flag == 'both' and entity1_coo and entity2_coo:
            print('SVB_VOB both coo')
            e1_coo_final = self.find_final_entity(entity1_coo)
            e2_coo_final = self.find_final_entity(entity2_coo)
            if e1_coo_final.dependency == 'SBV' and e2_coo_final.dependency == 'VOB':
                verbs = self.determine_relation_SVB(entity1_coo, entity2_coo)
        else:
            debug_logger.debug("ERROR: SBV_VOB entity_flag parameter value:{} is invalid!".format(entity_flag))
            # error_logger

        # e1_final = self.find_final_entity(entity1)
        # e2_final = self.find_final_entity(entity2)
        # if e1_final == 'SBV' and e2_final == 'VOB':
        #     verbs = self.determine_relation_SVB()
        #
        #
        # verbs = []
        # if ent1.dependency == 'SBV' and ent2.dependency == 'VOB':
        #     if entity_flag == 'subject':
        #         pass
        #         verbs = self.determine_relation_SVB(entity1_coo, entity2)
        #     elif entity_flag == 'object':
        #         pass
        #         verbs = self.determine_relation_SVB(entity1, entity2_coo)
        #     else:
        #         verbs = self.determine_relation_SVB(entity1, entity2)
        #     # entity_coo不为空，存在并列
        #     # if entity_coo:
        #     #     if entity_flag == 'subject':
        #     #         return self.determine_relation_SVB(entity_coo, entity2, ent1, ent2)
        #     #     else:
        #     #         return self.determine_relation_SVB(entity1, entity_coo, ent1, ent2)
        #     # 非并列
        #     # else:
        #     #     return self.determine_relation_SVB(entity1, entity2, ent1, ent2, type2)
        #     # verbs = self.determine_relation_SVB(entity1, entity2)
        # # 习近平 主席 访问 奥巴马 总统 先生 -->先生 是 访问 的宾语，因此处理两层修饰
        # elif (ent1.dependency == 'SBV'
        #       and ent2.dependency == 'ATT' and ent2.head_word.dependency == 'VOB'
        #       and ent2.head_word.head == ent1.head):
        #     # entity_coo不为空，存在并列
        #     # if entity_coo:
        #     #     if entity_flag == 'subject':
        #     #         return self.determine_relation_SVB(entity_coo, entity2, ent1, ent2)
        #     #     else:
        #     #         return self.determine_relation_SVB(entity1, entity_coo, ent1, ent2)
        #     # else:
        #     #     return self.determine_relation_SVB(entity1, entity2, ent1, ent2)
        #     verbs = self.determine_relation_SVB(entity1, entity2)
        # # 奥巴马 总统 先生 访问 习近平 主席
        # elif (ent2.dependency == 'VOB'
        #       and ent1.dependency == 'ATT' and ent1.head_word.dependency == 'SBV'
        #       and ent1.head_word.head == ent2.head):
        #     # if entity_coo:
        #     #     pass
        #     # else:
        #     #     print("find the the the")
        #     #     return self.determine_relation_SVB(entity1, entity2, ent1, ent2)
        #     verbs = self.determine_relation_SVB(entity1, entity2)
        # # 奥巴马 总统 先生 访问 习近平 主席 同志
        # elif (ent1.dependency == 'ATT' and ent2.dependency == 'ATT'
        #       and ent1.head_word.dependency == 'SBV' and ent2.head_word.dependency == 'VOB'
        #       and ent1.head_word.head == ent2.head_word.head):
        #     # if entity_coo:
        #     #     pass
        #     # else:
        #     #     print('find two two two ')
        #     #     return self.determine_relation_SVB(entity1, entity2, ent1, ent2)
        #     verbs = self.determine_relation_SVB(entity1, entity2)
        for i, v in enumerate(verbs):
            relation_list = []
            relation_list.append(v)
            if i == 0:
                debug_logger.debug("-"*10+"SVB DSNF2"+'-'*10)
            else:
                debug_logger.debug("-"*10+"SVB verb coo DSNF7"+'-'*10)
            self.build_triple(entity1_list, entity2_list, relation_list)
        return False
        return False


    # def determine_relation_SVB(self, entity1, entity2, ent1, ent2, entity_coo=None, type='Other'):
    def determine_relation_SVB(self, entity1, entity2, type='Other'):
        """确定主语和宾语之间的关系
        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
            ent1: WordUnit，处理偏正结构后的实体1
            ent2: WordUnit，处理偏正结构后的实体2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        relation_list = []  # 关系列表
        debug_logger.debug("! determine_relation_SVB function: e1:{}, e2:{}".format(entity1,entity2))
        # relation_list.append(ent2.head_word)
        # relation_list.append(ent1.head_word)
        # ？？？为什么可以直接确定rela      tionship word，而不是遍历去寻找，在这里肯定有错误啊。
        # ----------------------------------------++++--------------------------------
        # 例如：习近平 主席 访问 奥巴马 总统 先生。 抽取得到的relation word是先生，而不是访问

        # # 根据SBV_VOB函数已经确定一定有SBV关系，因此深度遍历寻找relation
        # found_rel = False
        # tmp = entity1
        # while not found_rel:
        #     if tmp.dependency == 'SBV':
        #         relation_list.append(tmp.head_word)
        #         found_rel = True
        #     tmp = tmp.head_word
        # debug_logger.debug("Relation list: {}".format(" ".join([str(rel) for rel in relation_list])))

        # TODO; 需要根据 SVB_VOB函数的不同情况分别进行处理, 或者修改SVB_VOB传递过来的参数
        # 应该无论什么情况，先找到对应的dp中的符合的 主语 和 宾语 词

        # entity1_list = []  # 实体1列表
        # entity1_list.append(entity1)
        # entity2_list = []  # 实体2列表
        # entity2_list.append(entity2)
        #
        # # 实体补全(解决并列结构而增加)
        # # ent_1 = self.check_entity(entity1)
        # # ent_2 = self.check_entity(entity2)
        # # debug_logger.debug('determine_relation_SVB - 偏正修正部分：e1:{}, e2:{}'.format(ent1.lemma, ent2.lemma))
        # ent_1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        # ent_2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2
        # # 华盛顿 警方
        # # if ent_1 != entity1 and abs(ent_1.ID-entity1.ID) == 1 and (not self.is_entity(entity1.head_word)):
        # #     entity1_list.append(entity1.head_word)
        # # if ent_2 != entity2 and abs(ent_2.ID-entity2.ID) == 1 and (not self.is_entity(entity2.head_word)):
        # #     entity2_list.append(entity2.head_word)
        # if ent_1 != entity1 and abs(ent_1.ID - entity1.ID) == 1:
        #     entity1_list.append(ent_1)
        #     # 豫Ｆ××××× 号 重型 半挂⻋
        #     # 鄂Ｂ××××× 小轿车
        #     if ent_1.dependency == 'ATT' and abs(ent_1.head - entity1.ID) <= 3:
        #         entity1_list.append(ent_1.head_word)
        # if ent_2 != entity2 and abs(ent_2.ID - entity2.ID) == 1:
        #     entity2_list.append(ent_2)
        #     if ent_2.dependency == 'ATT' and abs(ent_2.head - entity2.ID) <= 3:
        #         entity2_list.append(ent_2.head_word)
        # print("process ent done")
        ent1 = self.check_entity(entity1)
        ent2 = self.check_entity(entity2)
        ent1 = self.find_final_entity(entity1)
        ent2 = self.find_final_entity(entity2)

        verbs = []  # 可能存在并列动词
        found_flag = False
        word_tmp = ent1
        while word_tmp and (not found_flag):
            # 张三视察并访问小明。
            # 张三视察并访问巴西。
            # 张三视察并访问Google。
            # 习近平主席视察厦门，李克强访问香港。
            # 实现1，2，3并解决 习近平 视察 香港 错误。
            if word_tmp.dependency == 'SBV':
                if word_tmp.head == ent2.head:
                    print("verb sat")
                    verbs.append(word_tmp.head_word)
                else:
                    verb_coos = []
                    verb_tmp = self.find_final_entity(ent2).head_word
                    # 找到与ent2相关的所有并列的verbs
                    while verb_tmp:
                        verb_coos.append(verb_tmp)
                        if verb_tmp.dependency == 'COO':
                            verb_tmp = verb_tmp.head_word
                        else:
                            break
                    print('aaa: verbs_coo: {}'.format(" ".join(str(word) for word in verb_coos)))
                    for verb in verb_coos:
                        is_verb_satify = True
                        # 如果verb存在宾语并且宾语不是ent2，不成立
                        for word_ID in range(verb.ID+1, ent2.ID):
                            w = self.sentence.get_word_by_id(word_ID)
                            if w.dependency=='VOB' and w.head_word==verb and w!=ent2:
                                is_verb_satify = False
                                break
                        # 如果verb的主语不是ent1，不成立
                        for word_ID in range(ent1.ID + 1, verb.ID):
                            w = self.sentence.get_word_by_id(word_ID)
                            if w.dependency=='SBV' and w.head_word==verb and w!=ent1:
                                is_verb_satify = False
                                break
                        # 将满足条件的verb加入verbs中
                        if is_verb_satify:
                            verbs.append(verb)
            word_tmp = word_tmp.head_word
        # 查找是否存在并列verb
        if len(verbs) > 0:
            id_tmp = verbs[0].ID
            while id_tmp < ent2.ID:
                word_tmp = self.sentence.get_word_by_id(id_tmp)
                if word_tmp.dependency == 'COO' and word_tmp.head_word == verbs[0]:
                    # 判断并列动词是否符合: 防止并列动词和第一个动词主语不同
                    satisfy = True
                    i = ent1.ID+1 # TODO； 应该可以替换为 i=verbs[0].ID 因为后一个动词即使有不同主语也是在第一个动词之后
                    while i < ent2.ID:  # 这里减1，因为ID从1开始编号
                        temp = self.sentence.get_word_by_id(i)
                        # if temp(entity) <-[SBV]- AttWord -[VOB]-> 'ent2'
                        if is_named_entity(temp) and temp.head == ent2.head and temp.dependency == 'SBV':
                            # 代词不作为实体对待
                            if temp.postag == 'r':
                                continue
                            else:
                                satisfy = False
                                break
                        i += 1
                    if satisfy:
                        verbs.append(word_tmp)
                    break
                id_tmp += 1

        debug_logger.debug("Found verbs: {}".format(" ".join([str(word) for word in verbs])))
        # for e1 in entity1_list:
        #     print('1'+str(e1))
        # for e2 in entity2_list:
        #     print('2'+str(e2))
        # for rel in relation_list:
        #     print('rel'+str(rel))

        return verbs
        for i, v in enumerate(verbs):
            relation_list = []
            relation_list.append(v)
            if i == 0:
                debug_logger.debug("-"*10+"SVB DSNF2"+'-'*10)
            else:
                debug_logger.debug("-"*10+"SVB verb coo DSNF7"+'-'*10)
            self.build_triple(entity1_list, entity2_list, relation_list)
        return False










        # 寻找relationship词
        coo_flag = True  # 主谓关系中，可以处理的标志位
        # 两个动词构成并列时候，为了防止实体的动作张冠李戴，保证第二个动宾结构不能直接构成SBV-VOB的形式
        # 否则不进行处理
        # 第二个谓词前面不能含有实体
        # 习近平主席视察并访问厦门 | 习近平主席视察厦门，李克强访问香港("视察"-[COO]->"访问")
        i = ent1.ID
        while i < ent2.ID - 1:  # 这里减1，因为ID从1开始编号
            temp = self.sentence.words[i]  # ent1的后一个词
            # if temp(entity) <-[SBV]- AttWord -[VOB]-> 'ent2'
            # 确保第二个动宾结构不能构成SBV-VOB的形式
            # TODO; 如何判断这个实体的类型？
            if is_named_entity(temp) and temp.head == ent2.head and temp.dependency == 'SBV':
                # 代词不作为实体对待
                if temp.postag == 'r':
                    continue
                else:
                    coo_flag = False
                    break
            i += 1


        # 如果coo_flag为False说明这两个实体不是和同一个verb有关系。
        if not coo_flag:
            print("exit coo_flag")
            return False
        else:
            print('enter coo_flag')
            relation_list = []
            found_rel = False
            tmp = entity1
            while not found_rel:
                if tmp.dependency == 'SBV':
                    relation_list.append(tmp.head_word)
                    found_rel = True
                tmp = tmp.head_word
            debug_logger.debug("Relation list: {}".format(" ".join([str(rel) for rel in relation_list])))

            if ent1.head == ent2.head:
                debug_logger.debug("-"*10+"SVB DSNF2"+'-'*10)
                self.build_triple(entity1_list, entity2_list, relation_list)
            if ent2.head_word.dependency == 'COO' and ent2.head_word.head == ent1.head:
                # 需要把两个动词都提取出来，因此可以抽取连个triple
                debug_logger.debug("-"*10+"SVB DSNF2"+'-'*10)
                self.build_triple(entity1_list, entity2_list, relation_list)
                relation_list = []
                found_rel = False
                tmp = entity2
                while not found_rel:
                    if tmp.dependency == 'VOB':
                        relation_list.append(tmp.head_word)
                        found_rel = True
                    tmp = tmp.head_word
                debug_logger.debug("Relation list: {}".format(" ".join([str(rel) for rel in relation_list])))
                debug_logger.debug("-"*10+"SVB COO DSNF7"+'-'*10)
                self.build_triple(entity1_list, entity2_list, relation_list)

            # if ent2.head_word.dependency == 'COO' and ent2.head_word.head_word.head == ent1.head:
            #     pass
                # self.build_triple()
        # TODO;

        return True

        is_ok = False  # 是否获得DSNF匹配
        if coo_flag:
            # [DSNF2]
            # 习近平 视察 厦门
            # 实体，关系前面已添加
            if ent1.head == ent2.head:
                is_ok = True  # 这里的标志位的含义转为是否存在可抽取的模式
            # [DSNF7]
            # 如果实体2所依存的词，与实体1所依存词构成COO，那么特征关系词选择实体2所依存的词
            # 习近平 视察 并 访问 厦门
            # 实体，关系前面已添加，这里谓词只取ent2的中心词("访问")
            elif (ent2.head_word.dependency == 'COO'
                  and (ent2.head_word.head == ent1.head  # 两个并列谓词
                       or ent2.head_word.head_word.head == ent1.head)):  # 三个并列谓词
                is_ok = True

        # 针对特殊情况进行后处理
        if coo_flag:
            # 如果特征关系词前面还有一个动词修饰它的话，两个词合并作为特征关系词，如"无法承认"
            temp = self.sentence.words[ent2.head - 2]  # 例如："无法"
            if temp.postag == 'v' and ent2.head_word.postag == 'v' and temp.head == ent2.head:
                relation_list.insert(0, temp)
            return self.build_triple(entity1_list, entity2_list, relation_list)
        return False

    # def coordinate(self, entity1, entity2):
    #     """[DSNF3|DSNF5|DSNF6]
    #         并列实体
    #         当实体存在COO时，如果实体1与实体2并列，实体2与实体3构成三元组，则实体1和实体2也会构成三元组
    #     Args:
    #         entity1: WordUnit，原实体1
    #         entity2: WordUnit，原实体2
    #     Returns:
    #         *: bool，获得三元组(True)，未获得三元组(False)
    #     """
    #     # ent1 = self.check_entity(entity1)
    #     # ent2 = self.check_entity(entity2)
    #     # debug_logger.debug('coordinate - 偏正修正部分：e1:{}, e2:{}'.format(ent1.lemma, ent2.lemma))
    #     ent1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
    #     ent2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2
    #     # 习近平 主席 和 李克强 总理 访问 美国
    #     # 依据"李克强"(entiy1)和"美国"(entity2)，抽取三元组(李克强, 访问, 美国)
    #     # 如果存在并列依存，只会有entity1(ent1) <-[ATT]- entity2(ent2)
    #     # entity1与entity2不构成主宾entity1(ent1) <-[ABV]- temp -[VOB]->entity3
    #     if ent1.dependency == 'COO' and (not self.SBV_VOB(entity1, entity2)):
    #         # 并列主语[DSNF5]
    #         # 定位需要entity1与entity3
    #         if ent1.head_word.dependency == 'SBV':
    #             # ent2所并列实体
    #             entity_subject = self.search_entity(ent1.head_word)
    #             if not self.SBV_VOB(entity_subject, entity2, entity_coo=entity1, entity_flag='subject'):
    #                 is_ok = self.SBVorFOB_POB_VOB(entity_subject, entity2, entity_coo=entity1, entity_flag='subject')
    #     # 习近平 访问 美国 和 英国
    #     # 依据"习近平"(entity1)和"英国"(entity2)，抽取三元组(习近平, 访问, 英国)
    #     elif ent2.dependency == 'COO' and (not self.SBV_VOB(entity1, entity2)):
    #         # 并列宾语[DSNF6]
    #         debug_logger.debug('---------并列宾语-------1')
    #         if ent2.head_word.dependency == 'VOB' or ent2.head_word.dependency == 'POB':
    #             # ent2所并列实体
    #             entity_object = self.search_entity(ent2.head_word)
    #             debug_logger.debug('---------并列宾语-------2'+str(entity1)+str(entity_object)+str(entity2))
    #             if not self.SBV_VOB(entity1, entity_object, entity_coo=entity2, entity_flag='object'):
    #                 debug_logger.debug('---------并列宾语-------3')
    #                 is_ok = self.SBVorFOB_POB_VOB(entity1, entity_object, entity_coo=entity2, entity_flag='object')
    #     return False

    def SBVorFOB_POB_VOB(self, entity1, entity2, entity_coo=None, entity_flag=''):
        """[DSNF3]
            实体1依存于V(SBV或前置宾语)，实体2依存于一个介词(POB)，且介词依存于V(ADV)，一个名词(将作为特征关系词)依存于Ｖ(VOB)
            习近平 对 埃及 进行 国事访问
        Args:
            entity1: WordUnit，原实体1("习近平")
            entity2: WordUnit，原实体2("埃及")
            entity2_coo: WordUnit，并列的entity2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        entity1_list = []
        entity2_list = []
        entity1_list.append(entity1)
        entity2_list.append(entity2)

        ent1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        ent2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2
        # 处理多级修饰
        if ent1 != entity1 and abs(ent1.ID - entity1.ID) == 1:
            entity1_list.append(ent1)
            if ent1.dependency == 'ATT' and abs(ent1.head - entity1.ID) <= 3:
                entity1_list.append(ent1.head_word)
        if ent2 != entity2 and abs(ent2.ID - entity2.ID) == 1:
            entity2_list.append(ent2)
            if ent2.dependency == 'ATT' and abs(ent2.head - entity2.ID) <= 3:
                entity2_list.append(ent2.head_word)

        # ent1 = self.check_entity(entity1)
        # ent2 = self.check_entity(entity2)
        # debug_logger.debug('SBVorFOB_POB_VOB - 偏正修正部分：e1:{}, e2:{}'.format(ent1.lemma, ent2.lemma))
        rels = []
        if ent1.dependency == 'SBV' or ent1.dependency == 'FOB':
            if ent2.dependency == 'POB' and ent2.head_word.dependency == 'ADV':
                if entity_coo:
                    if entity_flag == 'subject': # 主语并列
                        return self.determine_relation_SVP(entity_coo, entity2)
                    else: # 宾语并列
                        return self.determine_relation_SVP(entity1, entity_coo)
                else:
                    # return self.determine_relation_SVP(entity1, entity2, ent1, ent2)
                    rels = self.determine_relation_SVP(entity1, entity2)

        for i, relation_list in enumerate(rels):
            if i == 0:
                debug_logger.debug("-" * 10 + "SBVorFOB_POB_VOB DSNF3" + '-' * 10)
            else:
                debug_logger.debug("-" * 10 + "SBVorFOB_POB_VOB verb coo DSNF3" + '-' * 10)
            self.build_triple(entity1_list, entity2_list, relation_list)


        return False

    # def determine_relation_SVP(self, entity1, entity2, ent1, ent2):
    def determine_relation_SVP(self, entity1, entity2):
        """确定主语和宾语之间的关系
        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
            ent1: WordUnit，处理偏正结构后的实体1
            ent2: WordUnit，处理偏正结构后的实体2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        # relation_list = []  # 关系列表
        # relation_list.append(ent2.head_word.head_word)
        # relation_str = ent2.head_word.head_word.lemma  # 关系字符串

        # entity1_list = []
        # entity1_list.append(entity1)
        # entity2_list = []
        # entity2_list.append(entity2)
        #
        # # 实体补全(解决并列结构而增加)
        # # ent_1 = self.check_entity(entity1)
        # # ent_2 = self.check_entity(entity2)
        # # debug_logger.debug('determine_relation_SVP - 偏正修正部分：e1:{}, e2:{}'.format(ent1.lemma, ent2.lemma))
        # ent_1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        # ent_2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2
        #
        # if ent_1 != entity1 and abs(ent_1.ID - entity1.ID) == 1:
        #     entity1_list.append(ent_1)
        #     # 豫Ｆ×××××号重型半挂⻋
        #     if ent_1.dependency == 'ATT' and abs(ent_1.head - entity1.ID) <= 3:
        #         entity1_list.append(ent_1.head)
        # if ent_2 != entity2 and abs(ent_2.ID - entity2.ID) == 1:
        #     entity2_list.append(ent_2)
        #     if ent_1.dependency == 'ATT' and abs(ent_1.head - entity1.ID) <= 3:
        #         entity2_list.append(ent_1.head)

        ent1 = self.check_entity(entity1)
        ent2 = self.check_entity(entity2)
        verbs = [] # 可能存在并列动词: 如果并列的话确保是符合DSNF3结构的并列动词
        # NOTE: 根据ent2来寻找verb更合理
        found_flag = False
        word_tmp = ent2
        while word_tmp and (not found_flag):
            print('-------', str(word_tmp))
            # if word_tmp.head == ent1.head:
            if word_tmp.dependency == 'ADV':
                verbs.append(word_tmp.head_word)
                found_flag = True
            word_tmp = word_tmp.head_word
        debug_logger.debug("Found verbs: {}".format(" ".join([str(word) for word in verbs])))
        # 查找是否存在并列verb
        if len(verbs) > 0:
            id_tmp = verbs[0].ID
            while id_tmp < len(self.sentence.words)+1: # 这里动词在ent2的后面，区别于SBV-VOB结构
                word_tmp = self.sentence.get_word_by_id(id_tmp)
                if word_tmp.dependency == 'COO' and word_tmp.head_word == verbs[0]:
                    # 判断并列动词是否符合: 防止并列动词和第一个动词主语不同
                    satisfy = True
                    i = ent1.ID # TODO； 应该可以替换为 i=verbs[0].ID 因为后一个动词即使有不同主语也是在第一个动词之后
                    while i < ent2.ID-1:  # 这里减1，因为ID从1开始编号
                        temp = self.sentence.words[i]  # ent1的后一个词
                        # if temp(entity) <-[SBV]- AttWord -[VOB]-> 'ent2'
                        if is_named_entity(temp) and temp.head == ent2.head and temp.dependency == 'SBV':
                            # 代词不作为实体对待
                            if temp.postag == 'r':
                                continue
                            else:
                                satisfy = False
                                break
                        i += 1
                    if satisfy:
                        verbs.append(word_tmp)
                    break
                id_tmp += 1

        debug_logger.debug("Found verbs: {}".format(" ".join([str(word) for word in verbs])))

        # return False
        #
        #
        #
        #
        #
        #
        # word_tmp = ent1
        # while word_tmp and (not found_flag):
        #     if (word_tmp.dependency == 'SBV' or word_tmp.dependency == 'FOB') and ent2.head_word.head == word_tmp.head:
        #         verbs.append(word_tmp.head_word)
        #         found_flag = True
        #     # 中国国家主席习近平访问韩国，并在首尔大学发表演讲
        #     # if (word_tmp.dependency == 'COO') and ent2.head_word.head_word == word_tmp:
        #     #     verbs.append(word_tmp)
        #     #     found_flag = True
        #     word_tmp = word_tmp.head_word
        # id_tmp = verbs[0].ID
        # while id_tmp < len(self.sentence.words)+1:
        #    word_tmp = self.sentence.get_word_by_id(id_tmp)
        #    if word_tmp.dependency == 'COO' and word_tmp.head_word == verbs[0]:
        #        # 判断并列动词是否符合: 防止并列动词和第一个动词主语不同
        #        satisfy = True
        #        i = ent1.ID
        #        while i < ent2.ID - 1:  # 这里减1，因为ID从1开始编号
        #            temp = self.sentence.words[i]  # ent1的后一个词
        #            # if temp(entity) <-[SBV]- AttWord -[VOB]-> 'ent2'
        #            if is_named_entity(temp) and temp.head == ent2.head and temp.dependency == 'SBV':
        #                # 代词不作为实体对待
        #                if temp.postag == 'r':
        #                    continue
        #                else:
        #                    satisfy = False
        #                    break
        #            i += 1
        #        if satisfy:
        #            verbs.append(word_tmp)
        #        break
        #    id_tmp += 1
        #
        # debug_logger.debug("Found verbs: {}".format(" ".join([str(word) for word in verbs])))

        prep = ent2.head_word.lemma # 处理特殊介词
        verb_suppl = None
        id_tmp = verbs[0].ID
        while id_tmp < len(self.sentence.words) + 1:
            word_tmp = self.sentence.get_word_by_id(id_tmp)
            if word_tmp.dependency == 'VOB':
                verb_suppl = word_tmp
                break
            id_tmp += 1

        rels = []
        for i, v in enumerate(verbs):
            relation_list = []
            relation_list.append(v)
            if verb_suppl:
                relation_list.append(verb_suppl)

            rels.append(relation_list)

        return rels
        #     # 考虑特殊介词
        #     if prep == '被' or prep == '由':
        #         # TODO; 多个triples,不能使用return
        #         # return self.build_triple(entity2_list, entity1_list, relation_list)
        #         if i == 0:
        #             debug_logger.debug("-"*10+"SVP DSNF3"+'-'*10)
        #         else:
        #             debug_logger.debug("-"*10+"SVP coo DSNF3"+'-'*10)
        #         self.build_triple(entity2_list, entity1_list, relation_list)
        #     else:
        #         # return self.build_triple(entity1_list, entity2_list, relation_list)
        #         if i == 0:
        #             debug_logger.debug("-"*10+"SVP DSNF3"+'-'*10)
        #         else:
        #             debug_logger.debug("-" * 10 + "SVP coo DSNF3" + '-' * 10)
        #         self.build_triple(entity1_list, entity2_list, relation_list)
        # return False


        # exist_coo_verb = False
        # prep = ent2.head_word.lemma # 处理特殊介词
        # relation_list = []
        # if ent2.head_word.head == ent1.head:
        #     found_flag = False
        #     tmp = ent1
        #     while not found_flag:
        #         if tmp.dependency == 'SBV':
        #             relation_list.append(tmp)
        #             found_flag = True
        #         tmp = tmp.head_word
        #     while tmp.ID < len(self.sentence.words)+1:
        #         if tmp.dependency == 'VOB':
        #             relation_list.append(tmp)
        #             break
        #         tmp = self.sentence.get_word_by_id[tmp.ID+1]
        #         pass
        #
        # # 判断是否存在并列动词
        # # 习近平 在 上海 视察 和 监管。
        # if ent2.head_word.head_word
        #
        #
        # return False

        # 寻找动词并判断动词是否符合：动词，并列动词（符合），并列动词（不符合）
        coo_flag = False  # 并列动词是否符合要求标志位
        relation_word = None  # 关系词
        is_ok = False  # DSNF覆盖与否
        # 习近平 对 埃及 进行 国事访问
        if ent2.head_word.head == ent1.head:
            relation_word = ent1.head_word  # "进行"
            coo_flag = True  # 这里仅作为可处理标志
        # 上例的扩展，存在并列谓词时
        elif ent2.head_word.head_word.dependency == 'COO' and ent2.head_word.head_word.head == ent1.head:
            relation_word = ent2.head_word.head_word
            coo_flag = True
            # 两个动词构成并列时候，为了防止实体的动作张冠李戴，保证第二个动宾结构不能直接构成SBV-VOB的形式
            # 否则不进行处理
            i = ent1.ID
            while i < ent2.ID - 1:  # 这里减1，因为ID从1开始编号
                temp = self.sentence.words[i]  # ent1的后一个词
                # if temp(entity) <-[SBV]- AttWord -[VOB]-> 'ent2'
                if is_named_entity(temp) and temp.head == ent2.head and temp.dependency == 'SBV':
                    # 代词不作为实体对待
                    if temp.postag == 'r':
                        continue
                    else:
                        coo_flag = False
                        break
                i += 1

        # 如果满足动词并列要求
        if coo_flag:
            i = relation_word.ID  # 关系词的下一个位置("国事访问")索引下标
            while i < len(self.sentence.words):
                temp = self.sentence.words[i]  # "国事访问"
                # 关系词和temp相邻，并且temp的依存关系为"VOB"
                if temp.head_word == relation_word and temp.dependency == 'VOB':
                    relation_list.append(temp)  # 形成关系"进行国事访问"
                    relation_str += temp.lemma
                i += 1

            if len(relation_str) == 1:
                relation_list.append(ent2.head_word)

            prep = ent2.head_word.lemma
            # 如果介词为"被"或"由"，两个实体的位置要换一下
            if prep == '被' or prep == '由':
                return self.build_triple(entity2_list, entity1_list, relation_list)
            else:
                return self.build_triple(entity1_list, entity2_list, relation_list)
        return False

    def coordinate(self, entity1, entity2):
        """[DSNF3|DSNF5|DSNF6]
            并列实体
            当实体存在COO时，如果实体1与实体2并列，实体2与实体3构成三元组，则实体1和实体2也会构成三元组
        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        # ent1 = self.check_entity(entity1)
        # ent2 = self.check_entity(entity2)
        # debug_logger.debug('coordinate - 偏正修正部分：e1:{}, e2:{}'.format(ent1.lemma, ent2.lemma))
        # ent1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        # ent2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2
        ent1 = self.find_final_entity(entity1)
        ent2 = self.find_final_entity(entity2)

        if ent1.dependency == 'COO' and ent2.dependency == 'COO':
            e1_coo = ent1.head_word
            e2_coo = ent2.head_word
            if e1_coo.dependency == 'SBV' and e2_coo == 'VOB':
                pass
                self.SBV_VOB(entity1, entity2, entity1_coo=e1_coo, entity2_coo=e2_coo, entity_flag='both')
                # self.SBVorFOB_POB_VOB(self, entity1, entity2, entity_coo=None, entity_flag='')
        elif ent1.dependency == 'COO':
            e1_coo = ent1.head_word
            if e1_coo.dependency == 'SBV':
                print('Sub COO'+str(e1_coo))
                self.SBV_VOB(entity1, entity2, entity1_coo=e1_coo, entity_flag='subject')
                # self.SBVorFOB_POB_VOB(entity1, entity2, entity_coo=e1_coo, entity_flag='subject')
        elif ent2.dependency == 'COO':
            e2_coo = ent2.head_word
            if e2_coo.dependency == 'VOB':
                print('Obj COO'+str(e2_coo))
                self.SBV_VOB(entity1, entity2, entity2_coo=e2_coo, entity_flag='object')
                # self.SBVorFOB_POB_VOB(entity1, entity2, entity_coo=e2_coo, entity_flag='object')

        return False





        # 习近平 主席 和 李克强 总理 访问 美国
        # 依据"李克强"(entiy1)和"美国"(entity2)，抽取三元组(李克强, 访问, 美国)
        # 如果存在并列依存，只会有entity1(ent1) <-[ATT]- entity2(ent2)
        # entity1与entity2不构成主宾entity1(ent1) <-[ABV]- temp -[VOB]->entity3
        if ent1.dependency == 'COO' and (not self.SBV_VOB(entity1, entity2)):
            # 并列主语[DSNF5]
            # 定位需要entity1与entity3
            if ent1.head_word.dependency == 'SBV':
                # ent2所并列实体
                entity_subject = self.search_entity(ent1.head_word)
                if not self.SBV_VOB(entity_subject, entity2, entity_coo=entity1, entity_flag='subject'):
                    is_ok = self.SBVorFOB_POB_VOB(entity_subject, entity2, entity_coo=entity1, entity_flag='subject')
        # 习近平 访问 美国 和 英国
        # 依据"习近平"(entity1)和"英国"(entity2)，抽取三元组(习近平, 访问, 英国)
        elif ent2.dependency == 'COO' and (not self.SBV_VOB(entity1, entity2)):
            # 并列宾语[DSNF6]
            debug_logger.debug('---------并列宾语-------1')
            if ent2.head_word.dependency == 'VOB' or ent2.head_word.dependency == 'POB':
                # ent2所并列实体
                entity_object = self.search_entity(ent2.head_word)
                debug_logger.debug('---------并列宾语-------2'+str(entity1)+str(entity_object)+str(entity2))
                if not self.SBV_VOB(entity1, entity_object, entity_coo=entity2, entity_flag='object'):
                    debug_logger.debug('---------并列宾语-------3')
                    is_ok = self.SBVorFOB_POB_VOB(entity1, entity_object, entity_coo=entity2, entity_flag='object')
        return False


    def E_NN_E(self, entity1, entity2):
        """[DSNF1]
            如果两个实体紧紧靠在一起，第一个实体是第二个实体的ATT，两个实体之间的词性为NNT(职位名称)
            实现范式一：

        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        type="DSNF1"
        # entity1 <--[ATT]-- temp <--[ATT]-- entity2
        # 美国 总统 奥巴马
        if entity1.dependency == 'ATT' and entity1.head_word.dependency == 'ATT' and entity1.head_word.head == entity2.ID:
            temp = self.sentence.words[entity1.ID]  # entity1的后一个词
            # 如果temp前还有其他名词修饰器修饰
            # 美国 前任 总统 奥巴马 | 中国 前任 主席 习近平
            # "美国" <-[ATT]- 主席    主席 <-[ATT]- 胡锦涛    前任 <--- 主席
            # "前任" <---> other noun-modifier
            if temp.head == entity1.head and temp.dependency == 'ATT':
                if 'n' in entity1.head_word.postag:
                    relation_list = []  # 关系列表，把多的修饰词都做为关系词，如上： rel-> "前任总统"
                    relation_list.append(temp)
                    relation_list.append(entity1.head_word)
                    debug_logger.debug("-" * 10 + "E_NN_E multi rels" + '-' * 10)
                    return self.build_triple(entity1, entity2, relation_list, type=type)
            else:
                # 美国 总统 奥巴马
                if 'n' in entity1.head_word.postag:
                    head_word = entity1.head_word
                    debug_logger.debug("-" * 10 + "E_NN_E rel" + '-' * 10)
                    return self.build_triple(entity1, entity2, entity1.head_word, type=type)
        # 美国 的 奥巴马 总统
        # "美国" <-[ATT]- "总统"    "奥巴马" <-[ATT]- "总统"
        # ID("奥巴马")-ID("美国")==2
        elif (entity1.dependency == 'ATT' and entity2.dependency == 'ATT'
              and entity1.head == entity2.head and abs(entity2.ID - entity1.ID) == 2):
            if 'n' in entity1.head_word.postag:
                debug_logger.debug("-"*10+"E_NN_E rel behind"+'-'*10)
                return self.build_triple(entity1, entity2, entity1.head_word, type=type)
        # 美国 总统 先生 奥巴马
        # 中国 的 主席 习近平
        # "美国" <-[ATT]- "总统"    "总统" <-[ATT]- "先生"    "先生" <-[ATT]- "奥巴马"
        # entity1.head_word.head_word.head == entity2.ID
        elif (entity1.dependency == 'ATT' and entity1.head_word.dependency == 'ATT'
              and entity1.head_word.head_word.dependency == 'ATT' and entity1.head_word.head_word.head == entity2.ID):
            if 'n' in entity1.head_word.head_word.postag:
                relation_list = []
                relation_list.append(entity1.head_word)
                if entity2.head_word:
                    # 第二个例子中：习近平的head_word是None，避免出现None
                    relation_list.append(entity2.head_word)
                debug_logger.debug("-"*10+"E_NN_E entity mul"+'-'*10)
                return self.build_triple(entity1, entity2, relation_list)
        return False


    def entity_de_entity_NNT(self, entity1, entity2):
        """形如"厦门大学的朱崇实校长"，实体+"的"+实体+名词
        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
        # ent_1 = self.check_entity(entity1)
        # ent_2 = self.check_entity(entity2)
        # debug_logger.debug('entity_de_entity_NNT - 偏正修正部分：e1:{}, e2:{}'.format(ent_1.lemma, ent_2.lemma))
        ent_1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        ent_2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2
        entity1_list = []
        entity1_list.append(entity1)
        entity2_list = []
        entity2_list.append(entity2)
        if ent_1 != entity1 and abs(ent_1.ID - entity1.ID) == 1:
            entity1_list.append(ent_1)
            # 豫Ｆ××××× 号 重型 半挂⻋
            # 鄂Ｂ××××× 小轿车
            if ent_1.dependency == 'ATT' and abs(ent_1.head - entity1.ID) <= 3:
                entity1_list.append(ent_1.head_word)
        if ent_2 != entity2 and abs(ent_2.ID - entity2.ID) == 1:
            entity2_list.append(ent_2)
            if ent_1.dependency == 'ATT' and abs(ent_1.head - entity1.ID) <= 3:
                entity2_list.append(ent_1.head_word)

        # 厦门大学的朱崇实校长
        ok = False
        if self.sentence.words[entity1.ID].lemma == '的':
            if (entity1.head == entity2.head or entity1.head_word.head == entity2.ID
                    and 'n' in entity1.head_word.postag and entity1.ID < entity1.head):
                if entity2.postag == 'nh' and abs(entity2.ID - entity1.ID) < 4:
                    self.build_triple(entity1, entity2, entity1.head_word)
                ok = True

        # 葛印楼所有的冀ＢXXXXXX号重型半挂车
        # 葛印楼所有的车辆冀ＢXXXXXX小轿车
        temp = None

        if entity1.head == entity2.ID:
            temp = entity2
        # 鄂ＢXXXXXX小轿车
        elif entity1.head == entity2.head:
            temp = entity2.head_word
        # 冀ＢXXXXXX 号 重型 半挂车
        elif entity2.head_word:
            if entity1.head == entity2.head_word.head:
                temp = entity2.head_word.head_word
        if temp:
            i = entity1.ID
            while i <= entity2.ID - 2:
                word = self.sentence.words[i]
                if word.lemma == '的' and word.dependency == 'RAD' and word.head_word.head == temp.ID:
                    relation_list = []
                    relation_list.append(word.head_word)
                    relation_list.append(word)
                    self.build_triple(entity1_list, entity2_list, relation_list)
                    ok = True
                    break
                i += 1
        return ok

