import logging
from django.test import TestCase
from EventExploreServer.component.open_relation_extraction.utils import loading_rules


debug_logger = logging.getLogger('debug')


def extract_by_rules(entity_pair, sentence):
    # TODO; 改成 e1 list, e2 list, rel list
    rules = loading_rules()
    triple = None
    debug_logger.debug("Extracting relation of entity pair: {}".format([entity.lemma for entity in entity_pair]))
    for idx, rule in enumerate(rules):
        if rule['type'] == 1:
            debug_logger.debug('Rule{}, type{}'.format(idx, 1))
            triple = e1ANDe2_to_rel(entity_pair, sentence, rule)
        elif rule['type'] == 2:
            debug_logger.debug('Rule{}, type{}'.format(idx, 2))
            triple = e1_to_relANDrel_to_e2(entity_pair, sentence, rule)
        elif rule['type'] == 3:
            debug_logger.debug('Rule{}, type{}'.format(idx, 3))
            triple = rel_to_e1ANDe2_to_rel(entity_pair, sentence, rule)
        elif rule['type'] == 4:
            debug_logger.debug('Rule{}, type{}'.format(idx, 4))
            triple = rel_to_e1ANDe2(entity_pair, sentence, rule)

    return triple


def get_dps(child, ancestor):
    pass


def recursive_find(i, dps, word, ret):
    # print(i, ret)
    if i == len(dps):
        ret.append(word)
        return
    for w, dep in word.child_words:
    # for w, dep in word['child_words']: # TEST
    #     print(i,dep, dps[i])
        if dps[i] == dep:
            recursive_find(i+1, dps, w, ret)


def e1ANDe2_to_rel(entity_pair, sentence, rule):
    """
    根据E1，E2寻找满足 E1 <- Rel -> E2  的Rel
    :param entity_pair:
    :param sentence:
    :param rule:
    :return:
    """
    e1, e2 = entity_pair
    rel_from_e1 = None
    rel_from_e2 = None

    word = e1
    for dp in rule['e1']['to_rel_dps']:
        if word.dependency != dp:
            rel_from_e1 = None
            break
        word = word.head_word
        rel_from_e1 = word

    word = e2
    for dp in rule['e2']['to_rel_dps']:
        if word.dependency != dp:
            rel_from_e2 = None
            break
        word = word.head_word
        rel_from_e2 = word

    if rel_from_e1 == rel_from_e2 and rel_from_e1 != None:
        debug_logger.debug("Triple: ({}, {}, {})".format(e1.lemma, rel_from_e1.lemma, e2.lemma))
        return (e1, rel_from_e1, e2)
    else:
        return None


def e1_to_relANDrel_to_e2(entity_pair, sentence, rule):
    """
    根据E1, E2寻找满足 E1 <- Rel <- E2 的Rel
    :param entity_pair:
    :param sentence:
    :param rule:
    :return:
    """
    e1, e2 = entity_pair
    rel_from_e1 = None
    # rel_from_e2 = None
    relsID_from_e2 = []

    word = e1
    for dp in rule['e1']['to_rel_dps']:
        if word.dependency != dp:
            rel_from_e1 = None
            break
        word = word.head_word
        rel_from_e1 = word

    word = e2
    # 递归查找, 找到所有满足的情况
    # i = 0
    # length = len(rule['rel']['to_e2_dps'])
    recursive_find(0, rule['rel']['to_e2_dps'], word, relsID_from_e2)
    # print('relsID_from_e2: ', relsID_from_e2)
    # for dp in rule['rel']['to_e2_dps']:
    #     if word.dependency != dp:
    #         rel_from_e2 = None
    #         break
    #     word = word.head_word
    #     rel_from_e2 = word

    for relID in relsID_from_e2:
        if rel_from_e1 == sentence.get_word_by_id(relID) and rel_from_e1 != None:
            debug_logger.debug("Triple: ({}, {}, {})".format(e1.lemma, rel_from_e1.lemma, e2.lemma))
            return (e1, rel_from_e1, e2)

    return None
    # if rel_from_e1 == rel_from_e2:
    #     debug_logger.debug("Triple: ({}, {}, {})".format(e1.lemma, rel_from_e1.lemma, e2.lemma))
    #     return (e1, rel_from_e1, e2)
    # else:
    #     return None


def rel_to_e1ANDe2_to_rel(entity_pair, sentence, rule):
    """
    根据E1, E2寻找满足 E1 -> Rel -> E2 的Rel
    :param entity_pair:
    :param sentence:
    :param rule:
    :return:
    """
    e1, e2 = entity_pair
    relsID_from_e1 = []
    rel_from_e2 = None

    word = e1
    recursive_find(0, rule['rel']['to_e1_dps'], word, relsID_from_e1)

    word = e2
    for dp in rule['e2']['to_rel_dps']:
        if word.dependency != dp:
            rel_from_e2 = None
            break
        word = word.head_word
        rel_from_e2 = word

    for relID in relsID_from_e1:
        if sentence.get_word_by_id(relID) == rel_from_e2 and rel_from_e2 != None:
            debug_logger.debug("Triple: ({}, {}, {})".format(e1.lemma, rel_from_e2.lemma, e2.lemma))
            return (e1, rel_from_e2, e2)
    else:
        return None


def rel_to_e1ANDe2(entity_pair, sentence, rule):
    """
    根据E1, E2寻找满足 E1 -> Rel <- E2 的Rel
    :param entity_pair:
    :param sentence:
    :param rule:
    :return:
    """
    e1, e2 = entity_pair
    relsID_from_e1 = []
    relsID_from_e2 = []

    word = e1
    recursive_find(0, rule['rel']['to_e1_dps'], word, relsID_from_e1)

    word = e2
    recursive_find(0, rule['rel']['to_e2_dps'], word, relsID_from_e2)

    # if rel_from_e1 == rel_from_e2:
    #     debug_logger.debug("Triple: ({}, {}, {})".format(e1.lemma, rel_from_e1.lemma, e2.lemma))
    #     return (e1, rel_from_e1, e2)
    # else:
    #     return None
    return None





class TestExtractRelationByRules(TestCase):

    def test_extract_by_rules(self):
        debug_logger.setLevel(logging.DEBUG)
        from ltp.utils import split_sentence
        from EventExploreServer.component import NLP
        from EventExploreServer.component.open_relation_extraction.extractor import Extractor1
        text = '''
                小明死于美国。 
                美国总统奥巴马访问中国。
                '''
        origin_sentences = split_sentence(text)
        nlp = NLP()
        lemmas, hidden = nlp.segment(origin_sentences)
        words_postag = nlp.postag(lemmas, hidden)
        words_nertag = nlp.nertag(words_postag, hidden)
        sentences = nlp.dependency(words_nertag, hidden)

        for i in range(len(origin_sentences)):
            extractor = Extractor1(origin_sentences[i], sentences[i])
            for entity_pair in extractor.entity_pairs:
                extract_by_rules(entity_pair.get_pair(), sentences[i])

        # entity_pair = (sentences[0].words[0], sentences[0].words[7])
        #
        # extract_by_rules(entity_pair, sentences[0])


    def test_recursive_find(self):
        dps = ['level1-a', 'level2-b']
        word1 = {'word':'w1', 'child_words':[]}
        word2 = {'word':'w2', 'child_words':[]}
        word3 = {'word':'w3', 'child_words':[]}
        word4 = {'word':'w4', 'child_words':[]}
        word5 = {'word':'w5', 'child_words':[]}
        word6 = {'word':'w6', 'child_words':[]}
        word7 = {'word':'w7', 'child_words':[]}

        word1['child_words'].append((word2, 'level1-a'))
        word1['child_words'].append((word4, 'level1-a'))
        word2['child_words'].append((word3, 'level2-b'))
        word4['child_words'].append((word7, 'level2-b'))

        ret = []
        recursive_find(0, dps, word1, ret)
        print(ret)
