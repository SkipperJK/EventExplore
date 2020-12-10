import os
from config import ENTITY_DIR


actor_name_list = []
sport_name_list = []
star_name_list = []
# 需要对外国人的中文名进行处理，（或者找到对应的外国名），保证一个人之后一个名字

with open(os.path.join(ENTITY_DIR, 'actor_name_list.txt'), 'r') as fr:
    actor_name_list = [entity.replace('\n', '') for entity in fr.readlines() if entity]

with open(os.path.join(ENTITY_DIR, 'sport_name_list.txt'), 'r') as fr:
    sport_name_list = [entity.replace('\n', '') for entity in fr.readlines() if entity]

with open(os.path.join(ENTITY_DIR, 'star_name_list.txt'), 'r') as fr:
    star_name_list = [entity.replace('\n', '') for entity in fr.readlines() if entity]


def pure_entity(entity):
    replace_chars = [' ', '.', '-', '·', '•', '）', ')']
    for ch in replace_chars:
        entity = entity.replace(ch, '')
    entity = entity.split('（')[0]
    entity = entity.split('(')[0]
    return entity


def all_entity_dict():
    """
    对已有的实体进行合并，同时处理多个名字表示同一个人的情况，并加上类型属性
    # 属性：names， types
    :return:
    """
    entity_dict = {}
    all_ents = {
            '演员': actor_name_list,
            '运动员': sport_name_list,
            '明星': star_name_list
        }

    for type, ents in all_ents.items():
        for ent in ents:
            pure_ent = pure_entity(ent)
            # print(ent,pure_ent)
            if pure_ent not in entity_dict:
                entity_dict[pure_ent] = {}
                entity_dict[pure_ent]['nicknames'] = []
                entity_dict[pure_ent]['types'] = []
            if ent != pure_ent:
                entity_dict[pure_ent]['nicknames'].append(ent)

            entity_dict[pure_ent]['types'].append(type)

    # 去重
    for ent, attrs in entity_dict.items():
        attrs['nicknames'] = list(set(attrs['nicknames']))
        attrs['types'] = list(set(attrs['types']))

    return entity_dict


if __name__ == '__main__':
    print(len(actor_name_list), len(sport_name_list), len(star_name_list))
    # w = '尚格·云顿'
    # print(pure_entity(w))


    entities = all_entity_dict()
    for k, v in entities.items():
        print(k, v)
    print(len(entities.keys()))




