import numpy as np

class WordGraph:
    """
    对triples中的word进行词频统计，并对每个word相关的文章进行统计
    TODO: 统计每个词的词频大小
    TODO: 对每个词对应的文章进行记录
    TODO; 设置类变量，对每次查找增量处理

    """
    def __init__(self):
        self.triples = []
        self.word_count = {}
        self.id2word = {}
        self.word2id = {}
        self.dictionary = []
        self.num_words = len(self.dictionary)
        self.adjacency_mat = []
        self.word_related_articles = []
        # self.dictionary = self.word_counting()
        # self.links = self.word_link()
        # self.word_related_articles = self.recording_related_articles()


    def __call__(self, triples, articles):
        if len(triples) <= 0: return
        self.triples += triples
        self.expand_dictionary(triples)
        self.word_link(triples)
        self.recording_related_articles(triples, articles)


    def expand_dictionary(self, triples):
        """

        :param triples:
        :return:
        """
        for triple in triples:
            if triple.e1_lemma not in self.dictionary:
                self.dictionary.append(triple.e1_lemma)
            if triple.e2_lemma not in self.dictionary:
                self.dictionary.append(triple.e2_lemma)
            if triple.relation_lemma not in self.dictionary:
                self.dictionary.append(triple.relation_lemma)
        for idx in range(self.num_words, len(self.dictionary)):
            word = self.dictionary[idx]
            self.id2word[idx] = word
            self.word2id[word] = idx
        self.num_words = len(self.dictionary)


    def word_link(self, triples):
        """
        判断是否有链接
        TODO 计算边的权重
        TODO; 是wordGraph还是三元组？？？
        :param triples:
        :return:
        """
        # 使用邻接矩阵的方法
        for i in range(len(self.adjacency_mat), len(self.dictionary)):
            self.adjacency_mat.append([])
        for triple in triples:
            idx_e1 = self.word2id[triple.e1_lemma]
            idx_e2 = self.word2id[triple.e2_lemma]
            idx_rel = self.word2id[triple.relation_lemma]
            if idx_rel not in self.adjacency_mat[idx_e1]:
                self.adjacency_mat[idx_e1].append(idx_rel)
            if idx_e1 not in self.adjacency_mat[idx_rel]:
                self.adjacency_mat[idx_rel].append(idx_e1)
            if idx_rel not in self.adjacency_mat[idx_e2]:
                self.adjacency_mat[idx_e2].append(idx_rel)
            if idx_e2 not in self.adjacency_mat[idx_rel]:
                self.adjacency_mat[idx_rel].append(idx_e2)

        # 使用矩阵的方法
        # link_mat = np.zeros((len(self.dictionary), len(self.dictionary)))
        # for triple in self.triples:
        #     idx_e1 = self.word2id[triple.e1_lemma]
        #     idx_e2 = self.word2id[triple.e2_lemma]
        #     idx_rel = self.word2id[triple.relation_lemma]
        #     link_mat[idx_e1][idx_rel] += 1
        #     link_mat[idx_rel][idx_e1] += 1
        #     link_mat[idx_rel][idx_e2] += 1
        #     link_mat[idx_e2][idx_rel] += 1
        # return link_mat


    def recording_related_articles(self, triples, articles):
        """
        TODO; 增量处理
        :return:
        """
        id2article = {}
        for art in articles:
            id2article[art.id] = art
        for i in range(len(self.word_related_articles), len(self.dictionary)):
            self.word_related_articles.append([])
        for triple in triples:
            docID = triple.docID
            idx_e1 = self.word2id[triple.e1_lemma]
            idx_e2 = self.word2id[triple.e2_lemma]
            idx_rel = self.word2id[triple.relation_lemma]
            if docID not in self.word_related_articles[idx_e1]:
                self.word_related_articles[idx_e1].append(id2article[docID])
            if docID not in self.word_related_articles[idx_e2]:
                self.word_related_articles[idx_e2].append(id2article[docID])
            if docID not in self.word_related_articles[idx_rel]:
                self.word_related_articles[idx_rel].append(id2article[docID])





