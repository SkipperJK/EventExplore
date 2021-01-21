import os
import json
from config import RULE_DIR
from django.test import TestCase


def loading_rules():
    rules = []
    file = os.path.join(RULE_DIR, 'rules.json')
    if os.path.exists(file):
        with open(file, 'r') as fr:
            rules = json.load(fr)
    return rules


def saving_rule(rule):
    rules = loading_rules()
    rules.append(rule)
    file = os.path.join(RULE_DIR, 'rules.json')
    with open(file, 'w') as fw:
        json.dump(rules, fw, ensure_ascii=False, indent=4)



class TestUtils(TestCase):

    def test_loading_rules(self):
        from pprint import pprint
        rules = loading_rules()
        pprint(rules)