from django.test import TestCase


class DependencyRule:
    def __init__(self, e1_rel_dep_info, e2_rel_dep_info):
        """
        根据dep info构建规则
        :param e1_rel_dep_info:
        :param e2_rel_dep_info:
        """
        # 记录e1和rel之间的依存路径
        self.e1_rel_direction = e1_rel_dep_info['direction']
        self.e1_rel_dep_path = e1_rel_dep_info['depPath']
        self.e1_rel_ancestor_idx = e1_rel_dep_info['ancestorIdx']
        # 记录e2和rel之间的依存路径
        self.e2_rel_direction = e2_rel_dep_info['direction']
        self.e2_rel_dep_path = e2_rel_dep_info['depPath']
        self.e2_rel_ancestor_idx = e2_rel_dep_info['ancestorIdx']
    # def __init__(self, e1_pos, e2_pos, e1_ner, e2_ner, rel_pos):
    #     pass
    #     self.e1_pos = e1_pos
    #     self.e2_pos = e2_pos
    #     self.e1_ner = e1_ner
    #     self.e2_ner = e2_ner
    #     self.rel_pos = rel_pos
    #     # self.rel_ner = rel_ner
    #     self.type = None # 四种
    # def __init__(self, type1, e1_rel_dep_path, type2, e2_rel_dep_path):
    #     self.type1 = type1
    #     self.type2 = type2
    #     # self.e1_rel_dep_path = e1_rel_dep_path
    #     # self.e2_rel_dep_path = e2_rel_dep_path
    #
    #     if self.type1 == 1:
    #         pass
    #     elif self.type1 == 2:
    #         pass
    #     else:
    #         pass
    #
    #     if self.type2 == 1:
    #         pass
    #     elif self.type2 == 2:
    #         pass
    #     else:
    #         pass



    def dep_to_string(self, entity, dep_path, direction, ancestor_idx):
        dp_string = entity
        if direction == 1:
            dp_string += '<-'
            if ancestor_idx == -1:
                dp_string += '<-'.join(dep_path)
                dp_string += '<-'
            else:
                dp_string += '<-'.join(dep_path[:ancestor_idx])
                dp_string += '<-'
                dp_string += dep_path[ancestor_idx]
                dp_string += '->'
                dp_string += '->'.join(dep_path[ancestor_idx+1:])
                dp_string += '->'
            # dp_string += 'RELATION'
        elif direction == 2:
            dp_string += '->'
            dp_string += '->'.join(dep_path)
            dp_string += '->'
            # dp_string += 'RELATION'
        dp_string += '关系词'
        return dp_string




    def to_string(self):
        rule_string = "Rule:\n"
        rule_string += '\t实体1到关系词的依存路径：'
        rule_string += self.dep_to_string('实体1', self.e1_rel_dep_path, self.e1_rel_direction, self.e1_rel_ancestor_idx)
        rule_string += '\n'
        rule_string += '\t实体2到关系词的依存路径：'
        rule_string += self.dep_to_string('实体2', self.e2_rel_dep_path, self.e2_rel_direction, self.e2_rel_ancestor_idx)
        return rule_string
        e1_to_rel = 'Entity1'
        # if self.e1_rel_direction == 1:
        #     e1_to_rel += '<-'
        #     if self.e1_rel_ancestor_idx == -1:
        #         tmp_dp_path = '<-'.join(self.e1_rel_dep_path[:self.e1_rel_ancestor_idx])
        #         tmp_dp_path += '<-'
        #         tmp_dp_path += self.e1_rel_dep_path[self.e1_rel_ancestor_idx]
        #         tmp_dp_path += '->'
        #         tmp_dp_path += '->'.join(self.e1_rel_dep_path[self.e1_rel_ancestor_idx+1:])
        #         e1_to_rel += tmp_dp_path
        #     else:
        #         tmp_dp_path = '<-'.join(self.e1_rel_dep_path)
        #         e1_to_rel += tmp_dp_path
        # elif self.e1_rel_direction == 2:
        #     e1_to_rel += '->'
        #     e1_to_rel += '->'.join(self.e1_rel_dep_path)


        e2_to_rel = ''
        e2_direction = '<-' if self.e2_rel_direction == 1 else '->'
        pass

    # def to_string(self):
    #     rule_string = ""
    #     rule_string += "(Entity1 "
    #     arrow_type = '<-' if self.type1 == 1 else '->'
    #     for dep in self.e1_rel_dep_path:
    #         rule_string += arrow_type
    #         rule_string += dep
    #     rule_string += " Relation "
    #     arrow_type = '<-' if self.type2 == 1 else '->'
    #     for dep in self.e2_rel_dep_path:
    #         rule_string += arrow_type
    #         rule_string += dep
    #     rule_string += " Entity2)"
    #     return rule_string

    def construct_rule(self):
        pass


if __name__ == '__main__':
    e1_rel_dep_info = {
        'direction': 1,
        'depPath': ['ATT', 'SBV'],
        'ancestorIdx': -1
    }
    e1_rel_dep_info = {
        'direction': 2,
        'depPath': ['ATT', 'SBV'],
        'ancestorIdx': -1
    }
    e1_rel_dep_info = {
        'direction': 1,
        'depPath': ['ATT','TT', 'EE', 'SBV'],
        'ancestorIdx': 1
    }
    e2_rel_dep_info = {
        'direction': 1,
        'depPath': ['ATT', 'VOB'],
        'ancestorIdx': -1
    }
    rule = DependencyRule(e1_rel_dep_info=e1_rel_dep_info, e2_rel_dep_info=e2_rel_dep_info)
    print(rule.to_string())