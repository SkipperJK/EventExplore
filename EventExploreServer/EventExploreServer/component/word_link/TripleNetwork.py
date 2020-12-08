import numpy as np

class TripleNetwork:
    """


    """
    def __init__(self):
        self.triples = []
        self.word_count = {}
        self.id2word = {}
        self.word2id = {}
        self.dictionary = []
        self.num_words = len(self.dictionary)
        self.adjacency_mat = []
        self.edge_word_mat = []
        self.word_related_articles = []
        # self.dictionary = self.word_counting()
        # self.links = self.word_link()
        # self.word_related_articles = self.recording_related_articles()


    def __call__(self, triples, articles):
        if len(triples) <= 0: return
        self.triples += triples
        print('TripleNetwork ..................')
        self.expand_dictionary(triples)
        self.word_link(triples)
        return self.to_neo4jData()
        # self.recording_related_articles(triples, articles)


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
            # if triple.relation_lemma not in self.dictionary:
            #     self.dictionary.append(triple.relation_lemma)
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
            self.edge_word_mat.append([])
        # for triple in triples:
        #     idx_e1 = self.word2id[triple.e1_lemma]
        #     idx_e2 = self.word2id[triple.e2_lemma]
        #     idx_rel = self.word2id[triple.relation_lemma]
        #     if idx_rel not in self.adjacency_mat[idx_e1]:
        #         self.adjacency_mat[idx_e1].append(idx_rel)
        #     if idx_e1 not in self.adjacency_mat[idx_rel]:
        #         self.adjacency_mat[idx_rel].append(idx_e1)
        #     if idx_rel not in self.adjacency_mat[idx_e2]:
        #         self.adjacency_mat[idx_e2].append(idx_rel)
        #     if idx_e2 not in self.adjacency_mat[idx_rel]:
        #         self.adjacency_mat[idx_rel].append(idx_e2)


        for triple in triples:
            # 每个点之间仅能有一条边存在
            idx_e1 = self.word2id[triple.e1_lemma]
            idx_e2 = self.word2id[triple.e2_lemma]
            if idx_e2 not in self.adjacency_mat[idx_e1]:
                self.adjacency_mat[idx_e1].append(idx_e2)
                self.edge_word_mat[idx_e1].append(triple.relation_lemma)
            if idx_e1 not in self.adjacency_mat[idx_e2]:
                self.adjacency_mat[idx_e2].append(idx_e1)
                self.edge_word_mat[idx_e2].append(triple.relation_lemma)



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

    def to_neo4jData(self):
        ret = {
            "results":[
                {
                    "columns": [],
                    "data": [
                        {
                            "graph": {
                                "nodes": [

                                ],
                                "relationships": [

                                ]
                            }
                        }
                    ]
                }
            ],
            "errors":[]
        }

        for word in self.dictionary:
            node = {}
            node['id'] = self.word2id[word]
            node['labels'] = ["Entity"]
            node['properties'] = {}
            node['properties']['word'] = word
            ret['results'][0]['data'][0]['graph']['nodes'].append(node)

        num = 100000
        for id1, rels in enumerate(self.adjacency_mat):
            for id2, rel in enumerate(rels):
                relationship = {}
                relationship['id'] = num
                num += 1
                relationship['type'] = self.edge_word_mat[id1][id2]
                relationship['startNode'] = str(id1)
                relationship['endNode'] = str(id2)
                relationship['properties'] = {}
                ret['results'][0]['data'][0]['graph']['relationships'].append(relationship)

        return ret



