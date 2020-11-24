import logging
from EventExploreServer.model.Word import WordUnit
from EventExploreServer.model.Triple import TripleUnit

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

    def is_entity(self, entry):
        self.false_ = """判断词单元是否实体
        Args:
            entry: WordUnit，词单元
        Returns:
            *: bool，实体(True)，非实体(False)
        """
        # 候选实体词性列表
        # 人名，机构名，地名，其他名词，缩略词
        entity_postags = {'nh', 'ni', 'ns', 'nz', 'j'}
        if entry.postag in entity_postags:
            return True
        else:
            return False

    def check_entity(self, entity):
        """处理偏正结构(奥巴马总统)，得到偏正部分(总统)，句子成分的主语或宾语 (中文普遍独特现象）
           奥巴马<-(ATT)-总统
           例如：奥巴马 总统 访问 中国。其中：奥巴马的偏正部分是 总统，总统在dp中和访问（verb）是SBV关系。
           "the head word is a entity and modifiers are called the modifying attributives"
           偏差修正构成NE，则进行标记。 例如：同济大学，对同济偏差修正（同济修饰大学）之后得到同济大学，同时同济大学NER标注为命名实体
           问题？？？？ --》 习近平主席：习近平修饰主席，但是习近平就是命名实体。后期修改：根据pos提取会有问题？因为会把主席这个词置为True
           #Solution： 其实不用判断是否是 机构实体 ，只需要对偏正结构标记即可，从而避免对偏正结构进行重复的关系元组提取。
        Args:
            entity: WordUnit，待检验的实体
        Returns:
            head_word or entity: WordUnit，检验后的实体
        """
        head_word = entity.head_word  # 中心词
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
                #return entity
                return None
        else:
            #return entity
            return None

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
            if self.is_entity(self.sentence.words[i]):
                num += 1
            i += 1
        return num

    def build_triple(self, entity1, entity2, relation):
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
                return self.build_triple(entity1, entity2, relations)
                # print(entity1.lemma + '\t' + relations[0].lemma + relations[1].lemma + '\t' + entity2.lemma)
        return False

    def SBV_VOB(self, entity1, entity2, entity_coo=None, entity_flag=''):
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
        # ent1 = self.check_entity(entity1)  # 偏正部分，若无偏正部分则就是原实体
        # ent2 = self.check_entity(entity2)
        # debug_logger.debug('SBV_VOB - 偏正修正部分：e1:{}, e2:{}'.format(ent1.lemma, ent2.lemma))
        ent1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        ent2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2

        if ent1.dependency == 'SBV' and ent2.dependency == 'VOB':
            # entity_coo不为空，存在并列
            if entity_coo:
                if entity_flag == 'subject':
                    return self.determine_relation_SVB(entity_coo, entity2, ent1, ent2)
                else:
                    return self.determine_relation_SVB(entity1, entity_coo, ent1, ent2)
            # 非并列
            else:
                return self.determine_relation_SVB(entity1, entity2, ent1, ent2)
        # 习近平 主席 访问 奥巴马 总统 先生 -->先生 是 访问 的宾语，因此处理两层修饰
        elif (ent2.dependency == 'ATT' and ent2.head_word.dependency == 'VOB'
              and ent2.head_word.head == ent1.head):
            # entity_coo不为空，存在并列
            if entity_coo:
                if entity_flag == 'subject':
                    return self.determine_relation_SVB(entity_coo, entity2, ent1, ent2)
                else:
                    return self.determine_relation_SVB(entity1, entity_coo, ent1, ent2)
            else:
                return self.determine_relation_SVB(entity1, entity2, ent1, ent2)
        return False

    def determine_relation_SVB(self, entity1, entity2, ent1, ent2):
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
        # relation_list.append(ent2.head_word)
        relation_list.append(ent1.head_word)
        # ？？？为什么可以直接确定relationship word，而不是遍历去寻找，在这里肯定有错误啊。----------------------------------------++++--------------------------------
        # 例如：习近平 主席 访问 奥巴马 总统 先生。 抽取得到的relation word是先生，而不是访问
        entity1_list = []  # 实体1列表
        entity1_list.append(entity1)
        entity2_list = []  # 实体2列表
        entity2_list.append(entity2)

        # 实体补全(解决并列结构而增加)
        # ent_1 = self.check_entity(entity1)
        # ent_2 = self.check_entity(entity2)
        # debug_logger.debug('determine_relation_SVB - 偏正修正部分：e1:{}, e2:{}'.format(ent1.lemma, ent2.lemma))
        ent_1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        ent_2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2
        # 华盛顿 警方
        # if ent_1 != entity1 and abs(ent_1.ID-entity1.ID) == 1 and (not self.is_entity(entity1.head_word)):
        #     entity1_list.append(entity1.head_word)
        # if ent_2 != entity2 and abs(ent_2.ID-entity2.ID) == 1 and (not self.is_entity(entity2.head_word)):
        #     entity2_list.append(entity2.head_word)
        if ent_1 != entity1 and abs(ent_1.ID - entity1.ID) == 1:
            entity1_list.append(ent_1)
            # 豫Ｆ××××× 号 重型 半挂⻋
            # 鄂Ｂ××××× 小轿车
            if ent_1.dependency == 'ATT' and abs(ent_1.head - entity1.ID) <= 3:
                entity1_list.append(ent_1.head)
        if ent_2 != entity2 and abs(ent_2.ID - entity2.ID) == 1:
            entity2_list.append(ent_2)
            if ent_1.dependency == 'ATT' and abs(ent_1.head - entity1.ID) <= 3:
                entity2_list.append(ent_1.head)

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
            if self.is_entity(temp) and temp.head == ent2.head and temp.dependency == 'SBV':
                # 代词不作为实体对待
                if temp.postag == 'r':
                    continue
                else:
                    coo_flag = False
                    break
            i += 1
        # 如果该句子满足处理要求
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
            elif (ent2.head_word.dependency == 'COO' and (ent2.head_word.head == ent1.head  # 两个并列谓词
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
        ent1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        ent2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2
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
        # ent1 = self.check_entity(entity1)
        # ent2 = self.check_entity(entity2)
        # debug_logger.debug('SBVorFOB_POB_VOB - 偏正修正部分：e1:{}, e2:{}'.format(ent1.lemma, ent2.lemma))
        ent1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        ent2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2
        if ent1.dependency == 'SBV' or ent1.dependency == 'FOB':
            if ent2.dependency == 'POB' and ent2.head_word.dependency == 'ADV':
                if entity_coo:
                    if entity_flag == 'subject':
                        return self.determine_relation_SVP(entity_coo, entity2, ent1, ent2)
                    else:
                        return self.determine_relation_SVP(entity1, entity_coo, ent1, ent2)
                else:
                    return self.determine_relation_SVP(entity1, entity2, ent1, ent2)
        return False

    def determine_relation_SVP(self, entity1, entity2, ent1, ent2):
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
        relation_list.append(ent2.head_word.head_word)
        relation_str = ent2.head_word.head_word.lemma  # 关系字符串

        entity1_list = []
        entity1_list.append(entity1)
        entity2_list = []
        entity2_list.append(entity2)

        # 实体补全(解决并列结构而增加)
        # ent_1 = self.check_entity(entity1)
        # ent_2 = self.check_entity(entity2)
        # debug_logger.debug('determine_relation_SVP - 偏正修正部分：e1:{}, e2:{}'.format(ent1.lemma, ent2.lemma))
        ent_1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        ent_2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2

        if ent_1 != entity1 and abs(ent_1.ID - entity1.ID) == 1:
            entity1_list.append(ent_1)
            # 豫Ｆ×××××号重型半挂⻋
            if ent_1.dependency == 'ATT' and abs(ent_1.head - entity1.ID) <= 3:
                entity1_list.append(ent_1.head)
        if ent_2 != entity2 and abs(ent_2.ID - entity2.ID) == 1:
            entity2_list.append(ent_2)
            if ent_1.dependency == 'ATT' and abs(ent_1.head - entity1.ID) <= 3:
                entity2_list.append(ent_1.head)

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
                if self.is_entity(temp) and temp.head == ent2.head and temp.dependency == 'SBV':
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

    def E_NN_E(self, entity1, entity2):
        """[DSNF1]
            如果两个实体紧紧靠在一起，第一个实体是第二个实体的ATT，两个实体之间的词性为NNT(职位名称)
        Args:
            entity1: WordUnit，原实体1
            entity2: WordUnit，原实体2
        Returns:
            *: bool，获得三元组(True)，未获得三元组(False)
        """
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
                    relation_list = []  # 关系列表
                    relation_list.append(temp)
                    relation_list.append(entity1.head_word)
                    return self.build_triple(entity1, entity2, relation_list)
            else:
                # 美国 总统 奥巴马
                if 'n' in entity1.head_word.postag:
                    head_word = entity1.head_word
                    return self.build_triple(entity1, entity2, entity1.head_word)
        # 美国 的 奥巴马 总统
        # "美国" <-[ATT]- "总统"    "奥巴马" <-[ATT]- "总统"
        # ID("奥巴马")-ID("美国")==2
        elif (entity1.dependency == 'ATT' and entity2.dependency == 'ATT'
              and entity1.head == entity2.head and abs(entity2.ID - entity1.ID) == 2):
            if 'n' in entity1.head_word.postag:
                return self.build_triple(entity1, entity2, entity1.head_word)
        # 美国 总统 先生 奥巴马
        # "美国" <-[ATT]- "总统"    "总统" <-[ATT]- "先生"    "先生" <-[ATT]- "奥巴马"
        # entity1.head_word.head_word.head == entity2.ID
        elif (entity1.dependency == 'ATT' and entity1.head_word.dependency == 'ATT'
              and entity1.head_word.head_word.dependency == 'ATT' and entity1.head_word.head_word.head == entity2.ID):
            if 'n' in entity1.head_word.head_word.postag:
                relation_list = []
                relation_list.append(entity1.head_word)
                relation_list.append(entity2.head_word)
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

