import logging
import copy
from django.test import TestCase
from pprint import pprint
from config import RULE_DIR
from EventExploreServer.component.open_relation_extraction.utils import saving_rule
from EventExploreServer.model import DependencyRule

debug_logger = logging.getLogger('debug')
trace_logger = logging.getLogger('trace')


def extract_rules(triples, sentence, save=False):
    """
    对triples中每个triple抽取可能存在的规则
    :param triples: list of TripleUnit
    :param sentence:
    :param save:
    :return:
    """
    rules = []
    trace_logger.info('\n' + sentence.to_string())
    for triple in triples:
        trace_logger.info(triple)
        rule = extract_rule(triple, sentence, save=save)
    #     if rule: rules.append(rule)
    # import os
    # with open(os.path.join(RULE_DIR, 'recording.txt'), 'a') as fw:
    #     fw.write(sentence.to_string() + "\n")
    #     for triple in triples:
    #         fw.write("HumanLabeled: {}\n".format(triple))
    #         fw.write("Rule: {}\n".format(rule.to_string() if rule else None))
    # return rules


def get_dp_root(sentence):
    root = None
    for word in sentence.words:
        if word.head_word == None:
            root = word
    return root


def find_sub_structure_root(entity_list, sentence):
    """
    对entity_list是句子dp树的一个子树，找出在子树中的根结点。
        对entity_list中的每个词进行广度/深度有限遍历（应该广度效果更好）
        如果子节点中包含entity_list，则将其放到非root list中
    :param entity_list:
    :param sentence:
    :return:
    """
    root = None
    if len(entity_list) == 1:
        root = entity_list[0]
    else:
        not_root_list = []
        for word in entity_list[::-1]:  # 对每个词进行广度优先遍历
            trace_logger.info('find_sub_structure_root, current word: {}'.format(word))
            if word in not_root_list: continue  # 如果已知非root，则继续
            # 对每个word进行BFS搜索
            word_queue = []
            include_words = []  # 记录该词为根结点的子树中包含的且在entity_list中的词
            word_queue.append(word)
            include_words.append(word)
            while len(word_queue) > 0:
                if len(include_words) == len(entity_list):
                    root = word
                    break
                tmp_word = word_queue.pop(0)
                for wordID, _ in tmp_word.child_words:
                    w = sentence.get_word_by_id(wordID)
                    if w in entity_list:
                        word_queue.append(w)
                        include_words.append(w)
                        if w not in not_root_list:
                            not_root_list.append(w)  # 作为某个词的子树中出现，一定不是root
    return root


def dfs_root_to_target_path(cur, target, sentence, path=[]):
    """
    找根结点到目标结点的路径
    :param cur:
    :param target:
    :param sentence:
    :param path:
    :return:
    """
    # path.append(cur.dependency)
    path.append(cur)  # 记录路径，有路径上的点组成
    if cur.ID == target.ID:
        return path
    if cur.child_words == []:
        return "no"
    for nodeID, _ in cur.child_words:
        t_path = copy.deepcopy(path)
        res = dfs_root_to_target_path(sentence.get_word_by_id(nodeID), target, sentence, t_path)
        if res == 'no':
            continue
        else:
            return res
    return "no"


def get_shortest_path(entity, relation, sentence):
    """
    找两个结点之间的路径
    :param entity:
    :param relation:
    :param sentence:
    :return:
    """
    root = get_dp_root(sentence)

    path1 = dfs_root_to_target_path(root, entity, sentence, [])
    path2 = dfs_root_to_target_path(root, relation, sentence, [])
    if path1 == 'no' or path2 == 'no':
        return "no dep path"
    trace_logger.info("合并前：")
    trace_logger.info("\tRoot到entity: {}".format("->".join([w.lemma for w in path1])))
    trace_logger.info("\tRoot到relation: {}".format("->".join([w.lemma for w in path2])))

    # 对两个路径， 从尾巴开始向头 找到最近的公共根结点，合并根结点
    len1, len2 = len(path1), len(path2)
    id_path1 = [word.ID for word in path1]
    id_path2 = [word.ID for word in path2]
    common_ancestor = None
    for i in range(len1 - 1, -1, -1):
        if id_path1[i] in id_path2:
            index = id_path2.index(id_path1[i])
            common_ancestor = path1[i]
            trace_logger.info("公共祖先结点idx：{}, word: {}".format(index, path1[i].lemma))
            path2 = path2[index:]  # 公共祖先到 end 的路径
            # path1 = path1[-1:i:-1]
            path1 = path1[i:]  # 公共祖先到 start 的路径
            break
    # for i in range(len1 - 1, -1, -1):
    #     if path1[i] in path2:
    #         index = path2.index(path1[i])
    #         print("公共祖先结点idx：{}, word: {}".format(index, path1[i].lemma))
    #         path2 = path2[index:]
    #         path1 = path1[-1:i:-1]
    #         break
    trace_logger.info("合并后：")
    trace_logger.info("\t到entity: {}".format("->".join([w.lemma for w in path1])))
    trace_logger.info("\t到relation: {}".format("->".join([w.lemma for w in path2])))

    # 得到最近的公共祖先结点，同时path1，path2 分别是由最近公共祖先结点到 start和end的路径
    # 现在假设start是entity1或者entity2， end就是relation： 需要根据情况，来判断rel的位置的方向问题。
    dep_info = {
        'direction': 1,
        'depPath': [],
        'ancestorIdx': -1
    }
    # 由于depPath记录：entity到relation的依存，path要需要逆转
    dep_path1 = [w.dependency for w in path1[1:][::-1]]
    dep_path2 = [w.dependency for w in path2[1:][::-1]]

    if common_ancestor.ID == relation.ID:
        # 如果公共祖先是relation情况，这时，也就说明方向是 relation -》entity， path1的路径就是entitty到relation路径
        dep_info['direction'] = 1
        dep_info['depPath'] += dep_path1
    elif common_ancestor.ID == entity.ID:
        # 如果公共祖先是entity的情况，这时，也就说明方向是 entity-》relation， path2的路径就是entitty到relation路径
        dep_info['direction'] = 2
        dep_info['depPath'] += dep_path2
    else:
        # 如果公共祖先是其他词，这时，也就说明方向是 entity <- common_ancestor -> relation
        dep_info['direction'] = 1
        dep_info['depPath'] += dep_path1
        dep_info['ancestorIdx'] = len(dep_info['depPath']) - 1
        dep_info['depPath'] += dep_path2

    print('DEPINFO: ', dep_info)
    return dep_info

    deps_info = {
        'type': -1,
    }
    if common_ancestor.ID == entity.ID:
        # 如果公共祖先是entity的情况，这时，也就说明方向是 entity-》relation
        pass
        deps_info['type'] = 1
        dep_path = []
        for w in path2[1:]:
            dep_path.append(w.dependency)
        deps_info['entity_to_relation'] = dep_path
    elif common_ancestor.ID == relation.ID:
        # 如果公共祖先是relation情况，这时，也就说明方向是 relation -》entity
        pass
        deps_info['type'] = 2
        dep_path = []
        for w in path1[1:]:
            dep_path.append(w.dependency)
        deps_info['relation_to_entity'] = dep_path
    else:
        # 如果公共祖先是其他词，这时，也就说明方向是 entity <- common_ancestor -> relation
        pass
        deps_info['type'] = 3
        ancestor_to_entity = []
        ancestor_to_relation = []
        for w in path1[1:]:
            ancestor_to_entity.append(w.dependency)
        for w in path2[1:]:
            ancestor_to_relation.append(w.dependency)
        deps_info['ancestor_to_entity'] = ancestor_to_entity
        deps_info['ancestor_to_relation'] = ancestor_to_relation

    return deps_info
    # print("dep path: ", deps)
    # res = path1 + path2
    # length = len(res)
    # return res


def extract_dep_info(entity1_root, relation_root, entity2_root, sentence):
    """
    找依存路径
    :param entity1_root:
    :param relation_root:
    :param entity2_root:
    :return:
    """
    entity1_relation_dep_info = get_shortest_path(entity1_root, relation_root, sentence)
    entity2_relation_dep_info = get_shortest_path(entity2_root, relation_root, sentence)
    return entity1_relation_dep_info, entity2_relation_dep_info


# Drop
def find_dep_with_relation_word(entity_list):
    """
    找出和关系词存在依赖的词
    :param entity_list:
    :return:
    """
    # 既然多个词可以组成一个实体，说明这个词之间肯定是相互修饰的，找到修饰的结构
    # 并且注意到被修饰的POS一般都是n（名词）
    # 找到被修饰的词，就可以用被修饰的词去跟relation找依赖关系
    # 同时：中文的习惯都是修饰词在前
    # 问题：中文中很多直接的主语（也不全是主语）并不是命名实体，而是命名实体修饰的一个名词，通常都是这个词和关系词存在依赖关系，
    #   因此，首先的目的是根据启发式规则抽取出这个词。
    # 或者说这个命名实体被分词了，仍然要找到这个存在的关系。  --》这种问题在抽取中不存在，因为抽取是对识别对命名实体对儿抽取关系
    # --》默认存在修饰，也就是其中的词的head_word词不在该list里面
    # 这样处理不对啊：美国 总统 特朗普 -》但是这之后一个word ----》先recording
    word = None
    if len(entity_list) == 1:
        word = entity_list[0]
    else:
        for w in entity_list:
            if w not in entity_list:
                word = w
                print('find dep with relation word')
    return word


def find_dep_path(word1, word2, sentence):
    """
    找出word1和word2之间的依存路径
    :param word1:
    :param word2:
    :param sentence:
    :return:
    """
    # 0: on-dep,  1: word1->word2  2:word2->word1
    type = 0
    dep_path = []
    # from word1 to word2
    word1_tmp = word1
    dps_tmp = []
    while word1_tmp.head_word:
        dps_tmp.append(word1_tmp.dependency)
        if word1_tmp.head_word == word2:
            dep_path = dps_tmp
            type = 1
            debug_logger.debug("From E to Rel dps: {}".format(dep_path))
            return type, dep_path
        else:
            word1_tmp = word1_tmp.head_word
    # from word2 to word1
    word2_tmp = word2
    dps_tmp = []
    while word2_tmp.head_word:
        dps_tmp.append(word2_tmp.dependency)
        if word2_tmp.head_word == word1:
            dep_path = dps_tmp
            type = 2
            debug_logger.debug("From Rel to E dps: {}".format(dep_path))
            return type, dep_path
        else:
            word2_tmp = word2_tmp.head_word
    return type, dep_path


def extract_rule(triple, sentence, save=False):
    """
    根据人工标记的关系元组，以及句子的dp，抽取/推导出对应的规则
    :param triple: TripleUnit
    :param sentence: Sentence
    :return:
    """

    # Version3
    e1_list = triple.entity1_list
    rel_list = triple.relationship_list
    e2_list = triple.entity2_list
    trace_logger.info("E1 list: {}".format([' '.join([word.lemma for word in e1_list])]))
    trace_logger.info("Rel list: {}".format([' '.join([word.lemma for word in rel_list])]))
    trace_logger.info("E2 list: {}".format([' '.join([word.lemma for word in e2_list])]))
    e1_root = find_sub_structure_root(e1_list, sentence)
    e2_root = find_sub_structure_root(e2_list, sentence)
    rel_root = find_sub_structure_root(rel_list, sentence)
    trace_logger.info("E1_root: {}, Rel_root: {}, E2_root: {}".format(e1_root.lemma, rel_root.lemma, e2_root.lemma))
    # print("E1_root: {}, Rel_root: {}, E2_root: {}".format(e1_root.lemma, rel_root.lemma, e2_root.lemma))
    info1, info2 = extract_dep_info(e1_root, rel_root, e2_root, sentence)
    trace_logger.info("Info1: {} \n Info2: {}".format(info1, info2))
    rule = DependencyRule(info1, info2)
    print(rule.to_string())
    # print("Info1: {} \n Info2: {}".format(info1, info2))
    return rule
    return True

    # Version2
    e1_list = triple.entity1_list
    rel_list = triple.relationship_list
    e2_list = triple.entity2_list

    e1_word = find_dep_with_relation_word(e1_list)
    e2_word = find_dep_with_relation_word(e2_list)

    # rel_list 不需要找词吧
    type1 = 0
    type2 = 0
    for word in rel_list:
        if type1 == 0:
            type1, e1_rel_dep_path = find_dep_path(e1_word, word, sentence)
        if type2 == 0:
            type2, e2_rel_dep_path = find_dep_path(e2_word, word, sentence)
    if type1 == 0 or type2 == 0:
        return None
    rule = DependencyRule(type1, e1_rel_dep_path, type2, e2_rel_dep_path)
    print('Rule:' + rule.to_string())
    return rule

    # Version1
    # 如何实现针对抽取规则的关系抽取程序。
    # 如何搜索？
    # Version1：从rel出去的两个边找？
    ## 如何，用什么结构来表示rule
    ## rule中存在多种指向可能，e1->rel, e1<-rel, e2->rel, e2<-rel
    rule = {}
    rule['e1'] = {}
    rule['e2'] = {}
    rule['rel'] = {}
    e1, rel, e2 = triple
    # can_extract_rule = True
    e1_to_rel_dps = []
    e2_to_rel_dps = []
    rel_to_e1_dps = []
    rel_to_e2_dps = []

    # From E1 to Rel
    e1_tmp = e1
    dps_tmp = []
    while e1_tmp.head_word:
        dps_tmp.append(e1_tmp.dependency)
        if e1_tmp.head_word == rel:
            e1_to_rel_dps = dps_tmp
            break
        else:
            e1_tmp = e1_tmp.head_word
    debug_logger.debug("From E1 to Rel dps: {}".format(e1_to_rel_dps))
    # From E2 to Rel
    e2_tmp = e2
    dps_tmp = []
    while e2_tmp.head_word:
        dps_tmp.append(e2_tmp.dependency)
        if e2_tmp.head_word == rel:
            e2_to_rel_dps = dps_tmp
            break
        else:
            e2_tmp = e2_tmp.head_word
    debug_logger.debug("From E2 to Rel dps: {}".format(e2_to_rel_dps))
    # From Rel to E1
    rel_tmp = rel
    dps_tmp = []
    while rel_tmp.head_word:
        dps_tmp.append(rel_tmp.dependency)
        if rel_tmp.head_word == e1:
            rel_to_e1_dps = dps_tmp
            break
        else:
            rel_tmp = rel_tmp.head_word
    debug_logger.debug("From Rel to E1 dps: {}".format(rel_to_e1_dps))
    # From Rel to E2
    rel_tmp = rel
    dps_tmp = []
    while rel_tmp.head_word:
        dps_tmp.append(rel_tmp.dependency)
        if rel_tmp.head_word == e2:
            rel_to_e2_dps = dps_tmp
            break
        else:
            rel_tmp = rel_tmp.head_word
    debug_logger.debug("From Rel to E2 dps: {}".format(rel_to_e2_dps))

    # 判断是否合理
    if (len(e1_to_rel_dps) > 0 or len(rel_to_e1_dps) > 0) and (len(e2_to_rel_dps) > 0 or len(rel_to_e2_dps) > 0):
        rule['e1']['postag'] = e1.postag
        rule['e2']['postag'] = e2.postag
        rule['rel']['postag'] = rel.postag

        rule['e1']['nertag'] = e1.nertag
        rule['e2']['nertag'] = e2.nertag
        rule['rel']['nertag'] = rel.nertag

        rule['e1']['to_rel_dps'] = e1_to_rel_dps if len(e1_to_rel_dps) > 0 else []
        rule['e2']['to_rel_dps'] = e2_to_rel_dps if len(e2_to_rel_dps) > 0 else []
        rule['rel']['to_e1_dps'] = rel_to_e1_dps if len(rel_to_e1_dps) > 0 else []
        rule['rel']['to_e2_dps'] = rel_to_e2_dps if len(rel_to_e2_dps) > 0 else []

        if len(e1_to_rel_dps) > 0 and len(e2_to_rel_dps) > 0:
            rule['type'] = 1
        elif len(e1_to_rel_dps) > 0 and len(rel_to_e2_dps) > 0:
            rule['type'] = 2
        elif len(rel_to_e1_dps) > 0 and len(e2_to_rel_dps) > 0:
            rule['type'] = 3
        elif len(rel_to_e1_dps) > 0 and len(rel_to_e2_dps) > 0:
            rule['type'] = 4

        pprint(rule)
        if save:
            saving_rule(rule)
        return rule
    else:
        return None


class TestRule(TestCase):

    def test_extract_rule(self):
        from ltp.utils import split_sentence
        from EventExploreServer.component.nlp_annotator.nlp import nlp
        debug_logger.setLevel(logging.DEBUG)
        text = '''
        哈德森出生在伦敦的郊区汉普斯特德。 
        美国总统奥巴马访问中国。
        美国总统特朗普对中国进行国事访问。 
        1927年3月11日，蒋介石、张静江、张群、黄山等人踏雪游览庐山风光。
        小鸟在水边寻食。
        '''
        origin_sentences = split_sentence(text)
        lemmas, hidden = nlp.segment(origin_sentences)
        print(lemmas)
        words_postag = nlp.postag(lemmas, hidden)
        words_nertag = nlp.nertag(words_postag, hidden)
        sentences = nlp.dependency(words_nertag, hidden)
        for sent in sentences:
            for word in sent.words:
                print(word.to_string())
            print(sent.get_name_entities())
        pass
        print("Test Extract Rule:")
        # save = True
        save = False
        from EventExploreServer.model import TripleUnit
        extract_rule(TripleUnit([sentences[0].words[0]], [sentences[0].words[1]], [sentences[0].words[6]]),
                     sentences[0], save)
        extract_rule(TripleUnit([sentences[1].words[0]], [sentences[1].words[1]], [sentences[1].words[2]]),
                     sentences[1], save)
        extract_rule(TripleUnit([sentences[1].words[2]], [sentences[1].words[3]], [sentences[1].words[4]]),
                     sentences[1], save)

        root = find_sub_structure_root([sentences[1].words[0], sentences[1].words[1], sentences[1].words[2]],
                                       sentences[1])
        print('Find root word: {}'.format(root))

        root = get_dp_root(sentences[3])
        p1 = dfs_root_to_target_path(root, sentences[3].words[4], sentences[3])
        for w in p1:
            print(w.lemma, end='-->')
        print()
        print("Test1: e1-蒋介石  rel-游览")
        get_shortest_path(sentences[3].words[4], sentences[3].words[15], sentences[3])
        print("Test2: e1-1927年  rel-踏雪")
        get_shortest_path(sentences[3].words[0], sentences[3].words[14], sentences[3])
        print("Test3: e1-踏雪  rel-1927年")
        get_shortest_path(sentences[3].words[14], sentences[3].words[0], sentences[3])
        print("Test4: e1-游览  rel-庐山")
        get_shortest_path(sentences[3].words[15], sentences[3].words[16], sentences[3])
        print("Test5: e1-庐山  rel-游览")
        get_shortest_path(sentences[3].words[16], sentences[3].words[15], sentences[3])
