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
        debug_logger.debug('Level 1: Init 偏正结构对应的中心词：E1: {:s}, E2: {:s}'.format(
            str(self.center_word_of_e1),
            str(self.center_word_of_e2)
        ))


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
            # if self.like_noun(head_word) and abs(entity.ID - head_word.ID) == 1:
            if self.like_noun(head_word) :
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
        else:
            return entity


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
        self.triples.append(TripleUnit(entity1, relation, entity2, type, self.idx_sentence, self.idx_document, self.num))
        self.num += 1
        triple = dict()
        # triple['num'] = self.num
        # self.num += 1
        triple['origin_sentence'] = self.origin_sentence
        entity1_str = self.element_connect(entity1)
        entity2_str = self.element_connect(entity2)
        relation_str = self.element_connect(relation)
        triple['knowledge'] = [entity1_str, relation_str, entity2_str]
        debug_logger.debug('Level 4: triple: ' + entity1_str + '\t' + relation_str + '\t' + entity2_str)
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
        entity1_list = []
        entity2_list = []
        entity1_list.append(entity1)
        entity2_list.append(entity2)
        relation_list = []
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
                    relation_list.append(temp)
                    relation_list.append(entity1.head_word)
                    debug_logger.debug("Level 2: " + "-" * 10 + "E_NN_E multi rels" + '-' * 10)
                    # return self.build_triple(entity1, entity2, relation_list, type=type)
                    self.build_triple(entity1_list, entity2_list, relation_list, type=type)
            else:
                # 美国 总统 奥巴马
                if 'n' in entity1.head_word.postag:
                    relation_list.append(entity1.head_word)
                    debug_logger.debug("Level 2: " + "-" * 10 + "E_NN_E rel" + '-' * 10)
                    # return self.build_triple(entity1, entity2, entity1.head_word, type=type)
                    self.build_triple(entity1_list, entity2_list, relation_list, type=type)
        # 美国 的 奥巴马 总统
        # "美国" <-[ATT]- "总统"    "奥巴马" <-[ATT]- "总统"
        # ID("奥巴马")-ID("美国")==2
        elif (entity1.dependency == 'ATT' and entity2.dependency == 'ATT'
              and entity1.head == entity2.head and abs(entity2.ID - entity1.ID) == 2):
            if 'n' in entity1.head_word.postag:
                relation_list.append(entity1.head_word)
                debug_logger.debug("Level 2: " + "-"*10+"E_NN_E rel behind"+'-'*10)
                # return self.build_triple(entity1, entity2, entity1.head_word, type=type)
                self.build_triple(entity1_list, entity2_list, relation_list, type=type)
        # 美国 总统 先生 奥巴马
        # 中国 的 主席 习近平
        # "美国" <-[ATT]- "总统"    "总统" <-[ATT]- "先生"    "先生" <-[ATT]- "奥巴马"
        # entity1.head_word.head_word.head == entity2.ID
        elif (entity1.dependency == 'ATT' and entity1.head_word.dependency == 'ATT'
              and entity1.head_word.head_word.dependency == 'ATT' and entity1.head_word.head_word.head == entity2.ID):
            if 'n' in entity1.head_word.head_word.postag:
                relation_list.append(entity1.head_word)
                if entity2.head_word:
                    # 第二个例子中：习近平的head_word是None，避免出现None
                    relation_list.append(entity2.head_word)
                debug_logger.debug("Level 2: " + "-"*10+"E_NN_E entity mul"+'-'*10)
                # return self.build_triple(entity1, entity2, relation_list)
                self.build_triple(entity1_list, entity2_list, relation_list, type=type)
        return False


    def SBV_CMP_POB(self, entity1, entity2, entity1_coo=None, entity2_coo=None, entity_flag=''):
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
        type = "DSNF4"
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

        relation_list = []
        e1_final = self.find_final_entity(entity1)
        e2_final = self.find_final_entity(entity2)
        e1_coo_final = self.find_final_entity(entity1_coo) if entity1_coo else None
        e2_coo_final = self.find_final_entity(entity2_coo) if entity2_coo else None
        if entity_flag == '':
            debug_logger.debug("Level 2: " + 'SBV_CMP_POB Normal')
            if e2_final.dependency == 'POB' and e2_final.head_word.dependency == 'CMP' \
                    and e1_final.dependency == 'SBV' and e1_final.head == e2_final.head_word.head:
                relation_list.append(e1_final.head_word)
                relation_list.append(e2_final.head_word)
                pass
        elif entity_flag == 'subject' and entity1_coo:
            debug_logger.debug("Level 2: " + 'SBV_CMP_POB sub coo')
            if e2_final.dependency == 'POB' and e2_final.head_word.dependency == 'CMP' \
                    and e1_coo_final.dependency == 'SBV' and e1_coo_final.head == e2_final.head_word.head:
                relation_list.append(e1_coo_final.head_word)
                relation_list.append(e2_final.head_word)
        elif entity_flag == 'object' and entity2_coo:
            debug_logger.debug("Level 2: " + 'SBV_CMP_POB obj coo')
            if e2_coo_final.dependency == 'POB' and e2_coo_final.head_word.dependency == 'CMP' \
                    and e1_final.dependency == 'SBV' and e1_final.head == e2_coo_final.head_word.head:
                relation_list.append(e1_final.head_word)
                relation_list.append(e2_coo_final.head_word)
        elif entity_flag == 'both' and entity1_coo and entity2_coo:
            debug_logger.debug("Level 2: " + 'SBV_CMP_POB both coo')
            if e2_coo_final.dependency == 'POB' and e2_coo_final.head_word.dependency == 'CMP' \
                    and e1_coo_final.dependency == 'SBV' and e1_coo_final.head == e2_coo_final.head_word.head:
                relation_list.append(e1_coo_final.head_word)
                relation_list.append(e2_coo_final.head_word)
        else:
            debug_logger.debug("Level 2: " + "ERROR: SBV_CMP_POB entity_flag parameter value:{} is invalid!".format(entity_flag))
            # error_logger

        if len(relation_list) > 0:
            self.build_triple(entity1_list, entity2_list, relation_list, type)
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
        type7 = "DSNF7"
        ent1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
        ent2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2

        entity1_list = []
        entity2_list = []
        entity1_list.append(entity1)
        entity2_list.append(entity2)
        # 处理多级修饰
        if ent1 != entity1:
        # if ent1 != entity1 and abs(ent1.ID - entity1.ID) == 1:
            entity1_list.append(ent1)
            if ent1.dependency == 'ATT' and abs(ent1.head - entity1.ID) <= 3:
                entity1_list.append(ent1.head_word)
        if ent2 != entity2:
        # if ent2 != entity2 and abs(ent2.ID - entity2.ID) == 1:
            entity2_list.append(ent2)
            if ent2.dependency == 'ATT' and abs(ent2.head - entity2.ID) <= 3:
                entity2_list.append(ent2.head_word)

        rels = []
        e1_final = self.find_final_entity(entity1)
        e2_final = self.find_final_entity(entity2)
        e1_coo_final = self.find_final_entity(entity1_coo) if entity1_coo else None
        e2_coo_final = self.find_final_entity(entity2_coo) if entity2_coo else None
        if entity_flag == '':
            debug_logger.debug("Level 2: " + 'SBV_VOB Normal')
            if e1_final.dependency == 'SBV' and e2_final.dependency == 'VOB':
                rels = self.determine_relation_SVB(entity1, entity2)
        elif entity_flag == 'subject' and entity1_coo:
            debug_logger.debug("Level 2: " + 'SBV_VOB sub coo')
            if e1_coo_final.dependency == 'SBV' and e2_final.dependency == 'VOB':
                rels = self.determine_relation_SVB(entity1_coo, entity2)
        elif entity_flag == 'object' and entity2_coo:
            debug_logger.debug("Level 2: " + 'SBV_VOB obj coo')
            if e1_final.dependency == 'SBV' and e2_coo_final.dependency == 'VOB':
                rels = self.determine_relation_SVB(entity1, entity2_coo)
        elif entity_flag == 'both' and entity1_coo and entity2_coo:
            debug_logger.debug("Level 2: " + 'SBV_VOB both coo')
            if e1_coo_final.dependency == 'SBV' and e2_coo_final.dependency == 'VOB':
                rels = self.determine_relation_SVB(entity1_coo, entity2_coo)
        else:
            debug_logger.debug("Level 2: " + "ERROR: SBV_VOB entity_flag parameter value:{} is invalid!".format(entity_flag))
            # error_logger

        for i, relation_list in enumerate(rels):
            if i == 0:
                debug_logger.debug("Level 4: " + "-"*10+"SVB DSNF2"+'-'*10)
                self.build_triple(entity1_list, entity2_list, relation_list, type2)
            else:
                debug_logger.debug("Level 4: " + "-"*10+"SVB verb coo DSNF7"+'-'*10)
                self.build_triple(entity1_list, entity2_list, relation_list, type7)
        return False


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
                    debug_logger.debug("Level 3: " + "verb satisfy")
                    verbs.append(word_tmp.head_word)
                else:
                    verb_coos = []
                    verb_tmp = ent2.head_word
                    # 找到与ent2相关的所有并列的verbs
                    while verb_tmp:
                        verb_coos.append(verb_tmp)
                        if verb_tmp.dependency == 'COO':
                            verb_tmp = verb_tmp.head_word
                        else:
                            break
                    debug_logger.debug("Level 3: " + 'find verbs_coo: {}'.format(" ".join(str(word) for word in verb_coos)))
                    for verb in verb_coos:
                        is_verb_satify = True
                        # 如果verb存在宾语并且宾语不是ent2，不成立
                        if verb.ID < ent1.ID: continue
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
                    debug_logger.debug("Level 3: " + 'satisfy verbs_coo: {}'.format(" ".join(str(word) for word in verbs)))
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

        debug_logger.debug("Level 3: " + "Found verbs: {}".format(" ".join([str(word) for word in verbs])))

        rels = []
        for i, v in enumerate(verbs):
            relation_list = []
            relation_list.append(v)
            rels.append(relation_list)
        return rels


    def SBVorFOB_POB_VOB(self, entity1, entity2, entity1_coo=None, entity2_coo=None,  entity_flag=''):
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
        type='DSNF3'
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

        rels = []
        prep = ''  # 考虑特殊介词'被' or '由':
        e1_final = self.find_final_entity(entity1)
        e2_final = self.find_final_entity(entity2)
        e1_coo_final = self.find_final_entity(entity1_coo) if entity1_coo else None
        e2_coo_final = self.find_final_entity(entity2_coo) if entity2_coo else None
        if entity_flag == '':
            debug_logger.debug("Level 2: " + 'SVB_POB_VOB Normal')
            if (e1_final.dependency == 'SBV' or e1_final.dependency == 'FOB')\
                    and e2_final.dependency == 'POB' and e2_final.head_word.dependency == 'ADV':
                rels, prep = self.determine_relation_SVP(entity1, entity2)
        elif entity_flag == 'subject' and entity1_coo:
            debug_logger.debug("Level 2: " + 'SBV_POB_VOB sub coo')
            if (e1_coo_final.dependency == 'SBV' or e1_coo_final.dependency == 'FOB') \
                    and e2_final.dependency == 'POB' and e2_final.head_word.dependency == 'ADV':
                rels, prep = self.determine_relation_SVP(entity1_coo, entity2)
        elif entity_flag == 'object' and entity2_coo:
            debug_logger.debug("Level 2: " + 'SBV_POB_VOB obj coo')
            if (e1_final.dependency == 'SBV' or e1_final.dependency == 'FOB') \
                    and e2_coo_final.dependency == 'POB' and e2_coo_final.head_word.dependency == 'ADV':
                rels, prep = self.determine_relation_SVP(entity1, entity2_coo)
        elif entity_flag == 'both' and entity1_coo and entity2_coo:
            debug_logger.debug("Level 2: " + 'SBV_POB_VOB both coo')
            if (e1_coo_final.dependency == 'SBV' or e1_coo_final.dependency == 'FOB') \
                    and e2_coo_final.dependency == 'POB' and e2_coo_final.head_word.dependency == 'ADV':
                rels, prep = self.determine_relation_SVP(entity1_coo, entity2_coo)
        else:
            debug_logger.debug("Level 2: " + "ERROR: SBV_POB_VOB entity_flag parameter value:{} is invalid!".format(entity_flag))
            # error_logger

        for i, relation_list in enumerate(rels):
            if i == 0:
                debug_logger.debug("Level 4: " + "-" * 10 + "SBVorFOB_POB_VOB DSNF3" + '-' * 10)
            else:
                debug_logger.debug("Level 4: " + "-" * 10 + "SBVorFOB_POB_VOB verb coo DSNF3" + '-' * 10)
            if prep == '被' or prep == '由':
                self.build_triple(entity2_list, entity1_list, relation_list, type)
            else:
                self.build_triple(entity1_list, entity2_list, relation_list, type)
        return False


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
        ent1 = self.find_final_entity(entity1)
        ent2 = self.find_final_entity(entity2)

        verbs = [] # 可能存在并列动词: 如果并列的话确保是符合DSNF3结构的并列动词
        # NOTE: 根据ent2来寻找verb更合理
        found_flag = False
        word_tmp = ent2
        while word_tmp and (not found_flag):

            if word_tmp.dependency == 'ADV':
                verbs.append(word_tmp.head_word)
                found_flag = True
            word_tmp = word_tmp.head_word
            # TODO; ent1 和 ent2 不是同一个动词

        debug_logger.debug("Level 3: " + "Found verbs: {}".format(" ".join([str(word) for word in verbs])))
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

        debug_logger.debug("Level 3: " + "Found verbs coo: {}".format(" ".join([str(word) for word in verbs])))
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
        return rels, prep


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
            e1_coo_final = self.find_final_entity(e1_coo)
            e2_coo_final = self.find_final_entity(e2_coo)
            if e1_coo_final.dependency == 'SBV' and e2_coo_final == 'VOB':
                debug_logger.debug("Level 2: " + "Sub COO AND Obj COO")
                self.SBV_VOB(entity1, entity2, entity1_coo=e1_coo, entity2_coo=e2_coo, entity_flag='both')
                self.SBVorFOB_POB_VOB(entity1, entity2, entity1_coo=e1_coo, entity2_coo=e2_coo, entity_flag='')
                self.SBV_CMP_POB(entity1, entity2, entity1_coo=e1_coo, entity2_coo=e2_coo, entity_flag='')
        elif ent1.dependency == 'COO':
            e1_coo = ent1.head_word
            e1_coo_final = self.find_final_entity(e1_coo)
            if e1_coo_final.dependency == 'SBV':
                debug_logger.debug("Level 2: " + 'Sub COO'+str(e1_coo))
                self.SBV_VOB(entity1, entity2, entity1_coo=e1_coo, entity_flag='subject')
                self.SBVorFOB_POB_VOB(entity1, entity2, entity1_coo=e1_coo, entity_flag='subject')
                self.SBV_CMP_POB(entity1, entity2, entity1_coo=e1_coo, entity_flag='subject')
        elif ent2.dependency == 'COO':
            e2_coo = ent2.head_word
            e2_coo_final = self.find_final_entity(e2_coo)
            if e2_coo_final.dependency == 'VOB' or e2_coo_final.dependency == 'POB': # DSNF2 和 DSNF3的宾语并列
                debug_logger.debug("Level 2: " + 'Obj COO'+str(e2_coo))
                self.SBV_VOB(entity1, entity2, entity2_coo=e2_coo, entity_flag='object')
                self.SBVorFOB_POB_VOB(entity1, entity2, entity2_coo=e2_coo, entity_flag='object')
                self.SBV_CMP_POB(entity1, entity2, entity2_coo=e2_coo, entity_flag='object')

        return False





    # def entity_de_entity_NNT(self, entity1, entity2):
    #     """形如"厦门大学的朱崇实校长"，实体+"的"+实体+名词
    #     Args:
    #         entity1: WordUnit，原实体1
    #         entity2: WordUnit，原实体2
    #     Returns:
    #         *: bool，获得三元组(True)，未获得三元组(False)
    #     """
    #     # ent_1 = self.check_entity(entity1)
    #     # ent_2 = self.check_entity(entity2)
    #     # debug_logger.debug('entity_de_entity_NNT - 偏正修正部分：e1:{}, e2:{}'.format(ent_1.lemma, ent_2.lemma))
    #     ent_1 = self.center_word_of_e1 if self.center_word_of_e1 else self.entity1
    #     ent_2 = self.center_word_of_e2 if self.center_word_of_e2 else self.entity2
    #     entity1_list = []
    #     entity1_list.append(entity1)
    #     entity2_list = []
    #     entity2_list.append(entity2)
    #     if ent_1 != entity1 and abs(ent_1.ID - entity1.ID) == 1:
    #         entity1_list.append(ent_1)
    #         # 豫Ｆ××××× 号 重型 半挂⻋
    #         # 鄂Ｂ××××× 小轿车
    #         if ent_1.dependency == 'ATT' and abs(ent_1.head - entity1.ID) <= 3:
    #             entity1_list.append(ent_1.head_word)
    #     if ent_2 != entity2 and abs(ent_2.ID - entity2.ID) == 1:
    #         entity2_list.append(ent_2)
    #         if ent_1.dependency == 'ATT' and abs(ent_1.head - entity1.ID) <= 3:
    #             entity2_list.append(ent_1.head_word)
    #
    #     # 厦门大学的朱崇实校长
    #     ok = False
    #     if self.sentence.words[entity1.ID].lemma == '的':
    #         if (entity1.head == entity2.head or entity1.head_word.head == entity2.ID
    #                 and 'n' in entity1.head_word.postag and entity1.ID < entity1.head):
    #             if entity2.postag == 'nh' and abs(entity2.ID - entity1.ID) < 4:
    #                 self.build_triple(entity1, entity2, entity1.head_word)
    #             ok = True
    #
    #     # 葛印楼所有的冀ＢXXXXXX号重型半挂车
    #     # 葛印楼所有的车辆冀ＢXXXXXX小轿车
    #     temp = None
    #
    #     if entity1.head == entity2.ID:
    #         temp = entity2
    #     # 鄂ＢXXXXXX小轿车
    #     elif entity1.head == entity2.head:
    #         temp = entity2.head_word
    #     # 冀ＢXXXXXX 号 重型 半挂车
    #     elif entity2.head_word:
    #         if entity1.head == entity2.head_word.head:
    #             temp = entity2.head_word.head_word
    #     if temp:
    #         i = entity1.ID
    #         while i <= entity2.ID - 2:
    #             word = self.sentence.words[i]
    #             if word.lemma == '的' and word.dependency == 'RAD' and word.head_word.head == temp.ID:
    #                 relation_list = []
    #                 relation_list.append(word.head_word)
    #                 relation_list.append(word)
    #                 self.build_triple(entity1_list, entity2_list, relation_list)
    #                 ok = True
    #                 break
    #             i += 1
    #     return ok

