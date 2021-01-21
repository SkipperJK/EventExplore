from ltp import LTP
from config import LTP4_MODEL_DIR
from EventExploreServer.component.nlp_annotator.nlp import nlp

class NLPLTP:

    def __init__(self, default_model_dir = LTP4_MODEL_DIR):
        print(default_model_dir)
        self.ltp = LTP(path=default_model_dir)





if __name__ == '__main__':
    ltp = LTP(path=LTP4_MODEL_DIR)
    seg, hidden = ltp.seg(["他叫汤姆去拿外衣。", "他就读于复旦大学。", "吴秀波diss李明", "新京报记者吴婷婷"])
    pos = ltp.pos(hidden)
    ner = ltp.ner(hidden)
    dep = ltp.dep(hidden)
    srl = ltp.srl(hidden)
    sdp = ltp.sdp(hidden)

    print('seg: ', seg)
    print('hidden', hidden)
    print('')
    print('pos: ', pos)
    print('ner: ', ner)
    print('dep: ', dep)
    print('srl: ', srl)
    print('sdp: ', sdp)

    origin_sentences = ["他叫汤姆去拿外衣。", "他就读于复旦大学。"]
    lemmas, hidden = nlp.segment(origin_sentences)
    words_postag = nlp.postag(lemmas, hidden)
    words_nertag = nlp.nertag(words_postag, hidden)
    sentences = nlp.dependency(words_nertag, hidden)
