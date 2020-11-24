from pymongo import MongoClient



conn = MongoClient('10.132.141.255', 27017)
db = conn['SinaNews']
collet = db['result_20191121']


corsor = collet.find({})


dist_cooccurence = {i:0 for i in range(5)}


    

for i, article in enumerate(corsor):
    print(i)
    if len(article['sentences']) == 1 and article['sentences'][0]['sentence'] == '':
        continue
    
    triggers = []
    idxs = []

    for j, sent in enumerate(article['sentences']):
        for k, word in enumerate(sent['words']):
            if word['postag'][0] != 'v':
                continue
            triggers.append(word['lemma'])
            idxs.append(j)
    
    for i in range(len(idxs)):
        for j in range(i+1, len(idxs)):
            if idxs[j] - idxs[i] >= 5:
                continue
            dist_cooccurence[idxs[j]-idxs[i]] += 1

    if i > 10000:
        break


for key, value in dist_cooccurence.items():
    print("%d: %d" % (key, value))


