from elasticsearch import helpers


def import_data2es(es, es_index, collection, bulk_size, field_mapping):
    """
    MongoDB数据导入到ES
    :param es_index:
    :param collection:
    :param field_mapping:
    :return:
    """
    cnt = 0
    cnt_all = 0
    actions = []
    all_time = 0
    for doc in collection.find().batch_size(bulk_size):
        doc['_id'] = str(doc['_id'])
        action = {}
        action = {
            "_op_type": "create",
            "_index": es_index,
            "_id": str(doc["_id"]),
            "_source": {}
        }
        for key, value in field_mapping.items():
            if key in doc:
                action["_source"][value] = doc[key]
            else:
                action["_source"][value] = {}

        # add in doc
        actions.append(action)
        if cnt_all != 0 and cnt_all % bulk_size== 0:
            try:
                helpers.bulk(es, actions=actions)
                print("Put successfully. Bulk " + str(cnt_all//bulk_size))
            except Exception as e:
                print(e)
                print("Got redundent items. Bulk " + str(cnt_all//bulk_size))
            del actions[0:len(actions)]
        cnt_all += 1
        #break

    if len(actions) != 0:
        try:
            helpers.bulk(es, actions=actions)
        except Exception as e:
            print("Got redundent items.")

    print("Finished." + str(cnt_all))

